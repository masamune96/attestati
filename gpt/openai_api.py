import sys
import json
import aiohttp
from utils.style import *
from utils.format import Formatter
from utils.config import openai_api_key
from utils.match_corsi import prompt_db
from gpt.tokens import shared
from openai import OpenAI

# capacità totale di token per richiesta (default: 128.000)
MAX_TOTAL_TOKENS = 128000
# numero massimo di token riservati all'output, per richiesta
MAX_OUTPUT_TOKENS = 16384
# margine di sicurezza per la dimensione del batch
BATCH_SAFETY_MARGIN = 0.1

# numero di token di output stimato per attestato (dipende dall'attestato)
TOKEN_OUTPUT_PER_PDF = 170


# openai client configuration
client = OpenAI(api_key=openai_api_key)

# prompt template
prompt = f"""
Ogni corso del database, quindi ogni riga, è espresso nella forma [CODICE CORSO] --- [NOME CORSO] (alias) --- [DURATA MINIMA - DURATA MASSIMA]
Ti invio inoltre un totale di N testi estratti da altrettanti attestati di partecipazione di dipendenti a corsi di formazione. 
Ogni testo è numerato e introdotto dalla dicitura "Attestato X - [nome_file]", dove X è il numero d'ordine dell'attestato nell'elenco nonchè l'id dell'attestato.
Rispondi SEMPRE con una lista [] che contenga come elementi ESATTAMENTE N JSON, uno per ciascuno degli attestati. A ciascun attestato deve essere associato il suo JSON, che non condivide con nessun altro attestato nell'elenco.
Esempio di output per N attestati: [{{json_attestato1}}, {{json_attestato2}}, ... {{json_attestatoN}}]
Il tuo output verrà elaborato automaticamente. Qualsiasi deviazione dal formato richiesto causerà errori nel sistema.

Usa questo formato esatto per il JSON di ciascun attestato:
{{
    "id": "<numero dell'attestato>",
    "nome_partecipante": "<nome proprio del partecipante>",
    "cognome_partecipante": "<cognome del partecipante>",
    "codice_fiscale": "<codice fiscale>",
    "data_fine_corso": "<data fine corso>",
    "nome_corso": "<nome del corso>",
    "codice_corso": "<codice corso>",
    "dati_anagrafici": "<YES/NO>",
    "tdi": "<YES/NO>",
    "durata_corso": "<durata>",
}}

Queste sono le regole da seguire alla lettera per elaborare gli attestati:
> Per ogni attestato nella richiesta, anche se duplicato, devi generare un JSON specifico nella riposta. Quindi se ricevi per esempio i testi di 10 attestati, dovrai SEMPRE ritornare 10 JSON associati.
> Se un dato manca tra quelli da compilare nel JSON dell'attestato, scrivi 'ND'.
> Analizza con attenzione tutti i dati prima di rispondere, la soglia di errore deve essere minima!
Compilazione JSON:
> Nel campo 'id' scrivi il numero dell'attestato ("<numero dell'attestato>" = "X" ricavato da "Attestato X - [nome_file]").
> Nome e cognome del partecipante devono essere separati e scritti ciascuno nelle apposite voci del JSON dell'attestato. Quindi in nome_partecipante devi scrivere il nome proprio del partecipante mentre in cognome_partecipante il cognome.
> Il codice fiscale deve essere alfanumerico di 16 caratteri (per esempio 'ZNLMTT94R21C618B' o 'ZNL MTT 94R21 C618B' ecc). Non accettare valori che non corrispondono ai formati.
> Per compilare correttamente la voce data_fine_corso:
    - La data_fine_corso, nel senso del periodo di effettivo svolgimento del corso, NON coincide necessariamente con la data di rilascio dell'attestato in coda al testo, che può essere successiva a quella di fine corso.
    - La data_fine_corso può essere riportata anche con termini quali "data registrazione verbale" o simili. Non considerare invece date non pertinenti quali, per esempio, quella di nascita per questo campo.
    - Conferma che la data_fine_corso sia in formato numerico gg/mm/aaaa, se è in un altro formato convertila.
> Il nome_corso, cioè il nome del corso di formazione dell'attestato, deve essere completo come indicato nel testo estratto.
> Per trovare il codice_corso:
    - Usa il database iniziale dei corsi di formazione per confrontare il corso dell'attestato.
    - Resta valida la forma [CODICE CORSO] --- [NOME CORSO] (alias) --- [DURATA MINIMA - DURATA MASSIMA] per l'estrapolazione del codice dal database.
    - In codice_corso devi riportare il migliore match possibile tra i codici corso presenti nel database con l'attestato analizzato, in base alle informazioni in tuo possesso.
    - La durata_corso DOVREBBE essere compresa tra la DURATA MINIMA e MASSIMA del corso selezionato nel database corsi.
    - Per attestati che hanno lo stesso "nome_corso", associa lo stesso "codice_corso".
    - In generale forza la scrittura del match migliore trovato, solo nel caso in cui non trovi nessun match soddisfacente riporta "ND".
> In dati_anagrafici scrivi 'YES' se nel testo dell'attestato è presente ALMENO UNO dei seguenti dati sul partecipante:
    - codice fiscale (alfanumerico di 16 caratteri, può contenere spazi e chiamato c.f. o simili)
    - data di nascita (in qualsasi formato)
    - luogo di nascita (nome di una città, provincia o stato)
    Se NESSUNO di questi dati è presente, scrivi 'NO'.
> In tdi scrivi 'YES' se nell'attestato è presente la dicitura 'tecnologie d'impresa' relativa all'erogatore del corso, altrimenti scrivi 'NO'.
> Scrivi la durata_corso così come compare nell'attestato (in numero ore), se non è presente scrivi 'ND'.
\n\n
"""

# tokens riservati per il prompt di sistema (assumo costante)
SYSTEM_PROMPT = shared.token_calculation(prompt+prompt_db)

# chiamata a openai API
async def openai_call(testi_batch, batch_size):

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    # prompt per openai
    prompt = f"""
Ogni corso del database, quindi ogni riga, è espresso nella forma [CODICE CORSO] --- [NOME CORSO] (alias) --- [DURATA MINIMA - DURATA MASSIMA]
Ti invio inoltre un totale di {batch_size} testi estratti da altrettanti attestati di partecipazione di dipendenti a corsi di formazione. 
Ogni testo è numerato e introdotto dalla dicitura "Attestato X - [nome_file]", dove X è il numero d'ordine dell'attestato nell'elenco nonchè l'id dell'attestato.
Rispondi SEMPRE con una lista [] che contenga come elementi ESATTAMENTE {batch_size} JSON, uno per ciascuno degli attestati. A ciascun attestato deve essere associato il suo JSON, che non condivide con nessun altro attestato nell'elenco.
Esempio di output per N attestati: [{{json_attestato1}}, {{json_attestato2}}, ... {{json_attestatoN}}]
Il tuo output verrà elaborato automaticamente. Qualsiasi deviazione dal formato richiesto causerà errori nel sistema.

Usa questo formato esatto per il JSON di ciascun attestato:
{{
    "id": "<numero dell'attestato>",
    "nome_partecipante": "<nome proprio del partecipante>",
    "cognome_partecipante": "<cognome del partecipante>",
    "codice_fiscale": "<codice fiscale>",
    "data_fine_corso": "<data fine corso>",
    "nome_corso": "<nome del corso>",
    "codice_corso": "<codice corso>",
    "dati_anagrafici": "<YES/NO>",
    "tdi": "<YES/NO>",
    "durata_corso": "<durata>",
}}

Queste sono le regole da seguire alla lettera per elaborare gli attestati:
> Per ogni attestato nella richiesta, anche se duplicato, devi generare un JSON specifico nella riposta. Quindi se ricevi per esempio i testi di 10 attestati, dovrai SEMPRE ritornare 10 JSON associati.
> Se un dato manca tra quelli da compilare nel JSON dell'attestato, scrivi 'ND'.
> Analizza con attenzione tutti i dati prima di rispondere, la soglia di errore deve essere minima!
Compilazione JSON:
> Nel campo 'id' scrivi il numero dell'attestato ("<numero dell'attestato>" = "X" ricavato da "Attestato X - [nome_file]").
> Nome e cognome del partecipante devono essere separati e scritti ciascuno nelle apposite voci del JSON dell'attestato. Quindi in nome_partecipante devi scrivere il nome proprio del partecipante mentre in cognome_partecipante il cognome.
> Il codice fiscale deve essere alfanumerico di 16 caratteri (per esempio 'ZNLMTT94R21C618B' o 'ZNL MTT 94R21 C618B' ecc). Non accettare valori che non corrispondono ai formati.
> Per compilare correttamente la voce data_fine_corso:
    - La data_fine_corso, nel senso del periodo di effettivo svolgimento del corso, NON coincide necessariamente con la data di rilascio dell'attestato in coda al testo, che può essere successiva a quella di fine corso.
    - La data_fine_corso può essere riportata anche con termini quali "data registrazione verbale" o simili. Non considerare invece date non pertinenti quali, per esempio, quella di nascita per questo campo.
    - Conferma che la data_fine_corso sia in formato numerico gg/mm/aaaa, se è in un altro formato convertila.
> Il nome_corso, cioè il nome del corso di formazione dell'attestato, deve essere completo come indicato nel testo estratto.
> Per trovare il codice_corso:
    - Usa il database iniziale dei corsi di formazione per confrontare il corso dell'attestato.
    - Resta valida la forma [CODICE CORSO] --- [NOME CORSO] (alias) --- [DURATA MINIMA - DURATA MASSIMA] per l'estrapolazione del codice dal database.
    - In codice_corso devi riportare il migliore match possibile tra i codici corso presenti nel database con l'attestato analizzato, in base alle informazioni in tuo possesso.
    - La durata_corso DOVREBBE essere compresa tra la DURATA MINIMA e MASSIMA del corso selezionato nel database corsi.
    - Per attestati che hanno lo stesso "nome_corso", associa lo stesso "codice_corso".
    - In generale forza la scrittura del match migliore trovato, solo nel caso in cui non trovi nessun match soddisfacente riporta "ND".
> In dati_anagrafici scrivi 'YES' se nel testo dell'attestato è presente ALMENO UNO dei seguenti dati sul partecipante:
    - codice fiscale (alfanumerico di 16 caratteri, può contenere spazi e chiamato c.f. o simili)
    - data di nascita (in qualsasi formato)
    - luogo di nascita (nome di una città, provincia o stato)
    Se NESSUNO di questi dati è presente, scrivi 'NO'.
> In tdi scrivi 'YES' se nell'attestato è presente la dicitura 'tecnologie d'impresa' relativa all'erogatore del corso, altrimenti scrivi 'NO'.
> Scrivi la durata_corso così come compare nell'attestato (in numero ore), se non è presente scrivi 'ND'.
\n\n
"""
    
    messaggi = [
        {
            "role": "system",
            "content": prompt_db + prompt
        },
        {
            "role": "user",
            "content": "\n\n".join([f"Attestato {i+1} - {nome_file}\n{text}" for i, (nome_file, text) in enumerate(testi_batch)])
        }
    ]
    payload = {
        "model": "gpt-4o",
        "messages": messaggi,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.0
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    response = await response.json()

                    # aggiorna i token utilizzati
                    shared.token(response)

                    # DEBUG
                    # print(json.dumps(response, indent=4))
                    # prompt_completo = messaggi[0]["content"] + messaggi[1]["content"]
                    # print(prompt_completo)

                    analisi = json.loads(Formatter.pulisci_output(response["choices"][0]["message"]["content"]))

                    # DEBUG JSON
                    if len(analisi) != len(testi_batch):
                        print(f"{RED}Attenzione: Numero di JSON restituiti ({len(analisi)}) non corrisponde al numero di attestati inviati ({len(testi_batch)}){RESET}")

                    return analisi
        
                else:
                    error_message = await response.text()
                    print(f"{RED}Errore API OpenAI:{RESET} {error_message}")
                    return []
                
    except Exception as e:
        error_message = str(e)
        print(f"\n{RED}{BOLD}Errore nell'elaborazione con OpenAI:{RESET} {e}")

        # errori di limits
        if "rate_limit_exceeded" in error_message or "429" in error_message:
            sys.exit(1)
        if "max_tokens" in error_message or "400" in error_message:
            sys.exit(1)
        return []




def crea_batch(testi_estratti):
    """
    Crea batch rispettando il limite totale di token per richiesta (input e output).
    - testi_estratti: Lista di dizionari con `nome_file`, `testo` e `token`.
    - return: Dimensione batch, batch.
    """

    max_input_tokens = int((MAX_TOTAL_TOKENS - MAX_OUTPUT_TOKENS - SYSTEM_PROMPT) * (1 - BATCH_SAFETY_MARGIN))
    max_output_tokens = int(MAX_OUTPUT_TOKENS * (1 - BATCH_SAFETY_MARGIN))

    batch_corrente = []
    token_corrente_input = 0

    for testo in testi_estratti:
        token_testo = testo["token"]
        token_output_stimati = TOKEN_OUTPUT_PER_PDF * (len(batch_corrente) + 1)

        # controlla se il batch supera i limiti di input o output
        if token_corrente_input + token_testo > max_input_tokens or token_output_stimati > max_output_tokens:
            # debug limite raggiunto
            # if token_corrente_input + token_testo > max_input_tokens:
            #    print(f"Limite di input raggiunto: {token_corrente_input + token_testo}/{max_input_tokens}")
            # if token_output_stimati > max_output_tokens:
            #    print(f"Limite di output raggiunto: {token_output_stimati}/{max_output_tokens}")
            
            yield len(batch_corrente), batch_corrente
            batch_corrente = []
            token_corrente_input = 0

        # aggiungi il testo al batch
        batch_corrente.append(testo)
        token_corrente_input += token_testo

    # ritorna l'ultimo batch, se esiste
    if batch_corrente:
        yield len(batch_corrente), batch_corrente
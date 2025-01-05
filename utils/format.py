import re

class Formatter:
    def valida_cf(cf):
        """
        Valida il codice fiscale seguendo il formato LLLLLLLNNLNNLNNNL.
        Risolve i problemi di 1 al posto di I e 0 al posto di O.
        """
        cf = cf.replace(" ", "").upper().strip()
        
        if len(cf) != 16:
            return "ND"
        
        # formato del codice fiscale (L lettera, N numero)
        formato = "LLLLLLNNLNNLNNNL"
        
        # correggi formato errato
        nuovo_cf = []
        for i, (char, tipo) in enumerate(zip(cf, formato)):
            if tipo == "L":
                if char.isdigit(): 
                    if char == "1":
                        nuovo_cf.append("I")
                    elif char == "0":
                        nuovo_cf.append("O")
                    else:
                        return "ND"
                else:
                    nuovo_cf.append(char)
            elif tipo == "N":
                if not char.isdigit():
                    if char == "I":
                        nuovo_cf.append("1")
                    elif char == "O":
                        nuovo_cf.append("0")
                    else:
                        return "ND"
                else:
                    nuovo_cf.append(char)
        return "".join(nuovo_cf)
    
    def pulisci_nome_corso(nome_corso):
        """
        Pulisce il nome del corso rimuovendo caratteri speciali e spazi multipli.
        Risolve i problemi di raggruppamento corsi per stesso corso.
        """
        if not nome_corso or nome_corso == "ND":
            return "ND"
        
        # rimuove caratteri non alfanumerici
        nome_corso = re.sub(r'[^A-Za-zÀ-ÿ0-9]+', ' ', nome_corso)
        nome_corso = re.sub(r'\s+', ' ', nome_corso)
        return nome_corso.strip()
    
    # pulisce output json openai
    def pulisci_output(output):
        output = re.sub(r"```json|```", "", output).strip()

        match = re.search(r'\[.*\]', output, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("JSON non trovato nell'output")
        
    # gestione bug #JSON < #Attestati
    def crea_placeholder(id_attestato):
        return {
            "id": f"{id_attestato}",
            "nome_partecipante": "ND",
            "cognome_partecipante": "ND",
            "codice_fiscale": "ND",
            "data_fine_corso": "ND",
            "nome_corso": "ND",
            "codice_corso": "ND",
            "dati_anagrafici": "ND",
            "tdi": "ND",
            "durata_corso": "ND"
        }
    
    def allinea_json(testi_batch, analisi_batch):
        """
        Allinea i JSON restituiti dal modello gpt agli attestati inviati.
        Aggiunge placeholder per eventuali JSON mancanti.
        """
        json_completi = []
        json_map = {int(json_item["id"]): json_item for json_item in analisi_batch}

        for i, attestato in enumerate(testi_batch, start=1):
            nome_attestato = attestato["nome_file"]
            if i in json_map:
                json_completi.append(json_map[i])
            else:
                print(f"Aggiunto JSON placeholder per l'attestato {i} ({nome_attestato}).")
                json_completi.append(Formatter.crea_placeholder(i))

        return json_completi
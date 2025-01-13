# ----- Valutazione MASSIMA in euro per richiesta OpenAI API -----
import os
import math
import requests
import tiktoken
from tqdm import tqdm  # progress bar
from utils.style import *
from utils.match_corsi import prompt_db
from OCR.text_extraction import estrai_google_vision
from concurrent.futures import ThreadPoolExecutor, as_completed

# prezzi in dollari per 1k tokens gpt-4o (da https://openai.com/api/pricing/)
PRICE_API_INPUT = 0.00250
PRICE_API_OUTPUT = 0.01000

# numero di token di output stimato per attestato (dipende dall'attestato)
TOKEN_OUTPUT_PER_PDF = 170
# numero di token processati per secondo (stima)
TOKEN_OUTPUT_RATE = 250


class SharedState:
    def __init__(self):
        self.token_totali = 0
        self.token_totali_input = 0
        self.token_totali_output = 0
        # dimensione batch da scrivere nella chiamata API (per bug numero JSON prodotti)
        self.current_batch_size = 0
        
        # tasso di cambio
        self._cached_rate = None
        
    @staticmethod
    def token_calculation(testo, model="gpt-4o"):
        """
        Calcola il numero di token di un testo utilizzando la tokenizzazione di OpenAI.
        Modello di default: gpt-4o.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(testo)
            return len(tokens)
        except Exception as e:
            print(f"Errore nel calcolo dei token: {e}")
            return 0
        
    # calcolo token
    def token(self, response):
        usage = response.usage
        self.token_totali += usage.total_tokens
        self.token_totali_input += usage.prompt_tokens
        self.token_totali_output += usage.completion_tokens

    def price_input(self):
        return ((self.token_totali_input / 1000) * PRICE_API_INPUT) / self.get_eur_to_usd_rate()
    def price_output(self):
        return ((self.token_totali_output / 1000) * PRICE_API_OUTPUT) / self.get_eur_to_usd_rate()
    def price(self):
        return round(self.price_input() + self.price_output(), 3)
    
    def token_per_pdf(self, pdf_folder):
        """
        Riceve una cartella con PDF.
        Ritorna una lista di dizionari con nome del file, testo e numero di token stimati.
        Mantiene l'ordine originale dei file.
        """
        pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

        def process_pdf(index, pdf_filename):
            """
            Elabora un singolo file PDF e include l'indice per mantenere l'ordine.
            """
            pdf_path = os.path.join(pdf_folder, pdf_filename)
            testo = estrai_google_vision(pdf_path)
            if testo and testo != "Errore":
                num_token = self.token_calculation(testo)
                return index, {
                    "nome_file": pdf_filename,
                    "testo": testo,
                    "token": num_token
                }

            return index, None

        # utilizzo del multithreading con mantenimento dell'ordine
        risultati = []
        max_workers = min(4, os.cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_pdf, i, pdf): pdf for i, pdf in enumerate(pdf_files)}
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"{BOLD}{GREEN}Elaborazione OCR{RESET} ({max_workers} threads)"):
                risultati.append(future.result())

        # ordina i risultati in base all'indice originale e filtra i `None`
        risultati_ordinati = [r[1] for r in sorted(risultati, key=lambda x: x[0]) if r[1] is not None]
        print()
        return risultati_ordinati
    
    # stima della durata della richiesta
    def stima_durata(self, testi_batch):
        """
        Stima il tempo di attesa in secondi.
        :param testi_batch: Testi batch
        :return: Durata stimata in secondi
        """
        token_input, token_output_stimati = self.stima_token(testi_batch)
        total_tokens = token_input + token_output_stimati
        tempo_stimato = math.ceil(total_tokens / TOKEN_OUTPUT_RATE)

        # print(f"\nTokens stimati: ~ {token_input + token_output_stimati}")
        # print(f"Tempo stimato: ~ {tempo_stimato} secondi\n")
        return tempo_stimato

    # calcola i token in input e stima quelli in output
    # const TOKEN_OUTPUT_PER_PDF settabile in base a num tokens output per attestato (stima)
    def stima_token(self, testi_batch):
        from gpt.openai_api import prompt
        contenuto_attestati = "\n\n".join([f"Attestato {i+1} - {nome_file}\n{text}" for i, (nome_file, text) in enumerate(testi_batch)])
        token_input = shared.token_calculation(prompt+prompt_db) + shared.token_calculation(contenuto_attestati)
        token_output_estimated = TOKEN_OUTPUT_PER_PDF * len(testi_batch)

        return token_input, token_output_estimated
    
    # tasso di cambio euro-dollaro
    def get_eur_to_usd_rate(self):
        """
        Ritorna il tasso di cambio EUR-USD utilizzando l'API di ExchangeRate-API.
        Salva il valore in una cache a partire dal tasso aggiornato al momento dell'esecuzione.
        Ritorna None se c'è un errore.
        """
        if self._cached_rate is not None:
            return self._cached_rate  
        try:
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            response = requests.get(url)
            data = response.json()
            self._cached_rate = data["rates"]["USD"] 
            return self._cached_rate
        except Exception as e:
            print(f"Errore nel recupero del tasso di cambio: {e}")
            return None


shared = SharedState()
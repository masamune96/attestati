import os
import openpyxl
from utils.style import *
from utils.format import Formatter
from utils.config import pdf_folder, excel_path
from gpt.tokens import shared
from gpt.openai_api import openai_call, crea_batch

def aggiorna_excel(excel_path, pdf_folder):
    try:
        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook.active

        # cerca prima riga con nome e cognome vuoti
        row = 1
        for current_row in range(1, sheet.max_row + 1):
            if (not sheet[f'B{current_row}'].value) and (not sheet[f'C{current_row}'].value):
                row = current_row
                break
        else:
            row = sheet.max_row + 1  

        # crea dizionario attestati con nome file, testo, num token per ogni attestato
        testi_estratti = shared.token_per_pdf(pdf_folder)

        batch_counter = 1

        # crea i batch basandosi sul calcolo dei token
        for batch in crea_batch(testi_estratti):
            try:
                print(f"{BOLD}Elaborando Batch {batch_counter} con {len(batch)} attestati{RESET}")
                analisi_batch = openai_call([(t["nome_file"], t["testo"]) for t in batch])

                # allinea i JSON agli attestati nel batch
                json_completi = Formatter.allinea_json(batch, analisi_batch)

                for i, attestato in enumerate(json_completi):
                    try:
                        nome_file = batch[i]["nome_file"]
                        testo_attestato = batch[i]["testo"]
                        nome_corso = Formatter.pulisci_nome_corso(attestato.get("nome_corso", "ND")).upper()
                        
                        # scrittura nell'excel
                        sheet[f'B{row}'] = attestato.get("nome_partecipante", "ND").upper()
                        sheet[f'C{row}'] = attestato.get("cognome_partecipante", "ND").upper()
                        sheet[f'D{row}'] = attestato.get("data_fine_corso", "ND")
                        sheet[f'E{row}'] = attestato.get("dati_anagrafici", "ND")
                        sheet[f'F{row}'] = Formatter.valida_cf(attestato.get("codice_fiscale", "ND"))
                        sheet[f'I{row}'] = attestato.get("tdi", "ND")
                        sheet[f'J{row}'] = nome_file
                        sheet[f'H{row}'] = attestato.get("codice_corso", "ND")
                        # DEBUG columns
                        sheet[f'T{row}'] = nome_corso
                        sheet[f'U{row}'] = testo_attestato
                        sheet[f'V{row}'] = str(attestato)

                        row += 1
                        
                    except Exception as e:
                        print(f"{RED}{BOLD}Errore durante la scrittura dei dati per {nome_file}:{RESET} {e}")
    
                batch_counter += 1

            except Exception as e:
                print(f"{RED}{BOLD}Errore durante l'elaborazione del batch:{RESET} {e}")
                raise RuntimeError(f"Errore critico nel Batch {batch_counter}: {e}")

        workbook.save(excel_path)
        print(f"\nDati aggiornati in {BOLD}{YELLOW}{excel_path}{RESET} \u2705\n")

    except Exception as e:
        print(f"{RED}{BOLD}Errore durante l'aggiornamento del file Excel:{RESET} {e}")





if __name__ == "__main__":
    if not os.path.exists(pdf_folder):
        print(f"{RED}{BOLD}Cartella PDF {pdf_folder} non trovata.{RESET}")
    else:
        aggiorna_excel(excel_path, pdf_folder)
        print(f"\U0001F9E9 Token totali: {BOLD}{shared.token_totali} ({shared.token_totali_input} input + {shared.token_totali_output} output){RESET}")
        print(f"\U0001F4B8 Costo totale: {BOLD}{shared.price()} \u20AC{RESET}")
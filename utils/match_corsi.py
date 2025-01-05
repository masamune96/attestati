# prompt_db (quindi il database dei corsi con codice, nome_corso e durata minima) è di circa 10k tokens, che equivale a circa 2 cent per richiesta
import pandas as pd
from utils.config import database_path

def carica_database_corsi(database_path):
    """
    Carica il database dei corsi da un file Excel.
    :param database_path: Percorso al file Excel.
    :return: DataFrame con i dettagli dei corsi.
    """
    columns_to_load = ["CODICE CORSO", "NOME CORSO", "alias", "DURATA MINIMA CORSO (ore)", "DURATA MASSIMA CORSO (ore)"]
    try:
        df_corsi = pd.read_excel(database_path, usecols=columns_to_load)
        return df_corsi
    except Exception as e:
        print(f"Errore nel caricamento del database: {e}")
        return None

def prompt_database():
    """
    Prepara il prompt includendo tutti i corsi con informazioni dettagliate.
    :return: Stringa formattata con l'elenco dei corsi.
    """
    database_corsi = carica_database_corsi(database_path)
    if database_corsi is None:
        return "Errore nel caricamento del database dei corsi."

    prompt_lines = []
    for _, row in database_corsi.iterrows():
        # costruisce una riga leggibile con tutte le informazioni del corso
        line = (
            f"{row['CODICE CORSO']} --- "
            f"{row['NOME CORSO']} "
            f"(alias: {row['alias'] if pd.notna(row['alias']) else 'ND'}) --- "
            f"{row['DURATA MINIMA CORSO (ore)']}-{row['DURATA MASSIMA CORSO (ore)']} ore\n"
        )
        prompt_lines.append(line)

    prompt_database = "\n".join(prompt_lines)

    prompt_database = f"""
Questo è un database di corsi di formazione:

{prompt_database}
"""
    return prompt_database

prompt_db = prompt_database()
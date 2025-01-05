from tqdm import tqdm
import time

# codici ANSI per stili e colori
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

# progress bar
def progress_bar(tempo_stimato, stop_loading):
    """
    Visualizza una barra di caricamento dinamica.
    :param tempo_stimato: Tempo stimato per il completamento
    :param stop_loading: Evento per fermare la barra
    """
    with tqdm(
        total=tempo_stimato,
        desc=f"{CYAN}Richiesta API in corso...{RESET} \u23F3",
        bar_format="{desc} {bar} Tempo trascorso: {elapsed} sec"
    ) as pbar:
        elapsed = 0
        while not stop_loading.is_set():
            time.sleep(1)
            elapsed += 1

            if pbar.n < tempo_stimato:
                pbar.update(1)
            else:
                pbar.refresh()

        if pbar.n < pbar.total:
            pbar.n = pbar.total
            pbar.refresh()
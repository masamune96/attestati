# Analisi Attestati

Questo progetto automatizza l'estrazione di testo da attestati PDF e utilizza OpenAI GPT per analizzare e organizzare i dati in un file Excel.

## **🚀 Funzionalità**

### Estrazione del testo dai PDF
- Utilizza **Google Vision OCR** per garantire un'estrazione accurata.
- Supporta PDF multipagina, convertendo le immagini in testo strutturato.

### Analisi del testo con `GPT-4o`
- Estrazione automatizzata di informazioni chiave:
  - **Nome del partecipante**
  - **Cognome del partecipante**
  - **Codice fiscale**
  - **Data di fine corso**
  - **Codice del corso**
- Validazione e pulizia dei dati (es. codice fiscale).
- Identificazione della presenza di **informazioni anagrafiche** e indicazioni sull'**organizzatore del corso**.

### Organizzazione dei dati in un file Excel
- Scrittura automatica dei dati estratti in colonne specifiche.
- Gestione degli errori per garantire coerenza nei risultati.

### Batching dei PDF
- Suddivisione dei PDF in batch per ottimizzare l'uso dei token e rispettare i limiti delle API.
- Gestione automatica dei batch con **margini di sicurezza** per evitare errori.

### Calcolo dei token e dei costi
- Analisi del numero totale di **token** utilizzati per input e output.
- Costo totale delle chiamate API di OpenAI in euro.

## **🔧 Prerequisiti**

### Ambiente di sviluppo
- **Python 3.8+**
- Ambiente virtuale (consigliato).

### Chiavi di accesso
- Una chiave JSON per **Google Vision**.
- Credenziali **OpenAI API**.

### Librerie richieste
- Installabili tramite il file `requirements.txt`.

## **📥 Installazione**

### 1️. Clona la repository
```bash
git clone https://github.com/masamune96/attestati.git
cd attestati
```

### 2️. Crea un ambiente virtuale e attivalo
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 3️. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4️. Configurazione OCR
Poppler è necessario per la conversione dei PDF in immagini.

  1. Scarica **Poppler** da [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows).
  2. Estrai i file e aggiungi il percorso della cartella `bin` alle variabili d'ambiente in `PATH`.

Imposta una variabile d'ambiente per **Google Vision**.
  1. Aggiungi una variabile d'ambiente di sistema con:
      - **name**: `GOOGLE_APPLICATION_CREDENTIALS`
      - **value**: percorso/al/file/`google_credentials.json`

### 5️. Configura il file `.env`
Aggiungi i seguenti valori:
```env
PDF_FOLDER=percorso/alla/cartella/pdf
EXCEL_PATH=percorso/al/file/excel
DATABASE_PATH=percorso/al/database/corsi
API_KEY=chiave_api_openai
POPPLER_PATH=percorso/alla/cartella/poppler/bin
GOOGLE_APPLICATION_CREDENTIALS=percorso/al/file/google_credentials.json
```

## **▶️ Esecuzione**
Esegui il programma principale con:
```bash
python attestati.py
```

Il programma:
1. Controlla che la cartella specificata contenga file PDF validi.
2. Estrae il testo da ciascun file PDF.
3. Analizza i dati utilizzando l'API **GPT-4o**.
4. Salva i risultati in un file Excel nel percorso configurato.
5. Fornisce un riepilogo dei **token utilizzati** e del **costo totale stimato**.

## **📂 Struttura del Progetto**

- **`attestati.py`**: Script principale per l'esecuzione del programma.
- **`openai_api.py`**: Gestione delle chiamate API a OpenAI e batching.
- **`text_extraction.py`**: Funzioni per l'estrazione del testo dai PDF.
- **`tokens.py`**: Calcolo dei token e gestione dei costi.
- **`config.py`**: Configurazione delle variabili di ambiente.
- **`format.py`**: Funzioni per la validazione e pulizia dei dati.
- **`style.py`**: Grafica console.

## **🛠️ Istruzioni dettagliate**

### 1. **Installare Python, Git e VS Code**

#### **Installare Python**
1. Vai su [python.org](https://www.python.org/downloads/) e scarica l'ultima versione di Python per Windows.
2. Avvia l’installer e seleziona:
   - **"Add Python to PATH"** (è una casella da spuntare all'inizio).
3. Premi su **Install Now** e segui il processo di installazione.
4. Una volta completato, verifica l'installazione:
   - Apri il terminale (Prompt dei comandi o PowerShell).
   - Digita:
     ```bash
     python --version
     ```
     Dovresti vedere qualcosa come `Python 3.x.x`.

#### **Installare Git**
  1. Vai su [git-scm.com](https://git-scm.com/) e scarica l'installer.
  2. Durante l'installazione:
      - Scegli "Use Git from the command line and also from 3rd-party software".
      - Lascia il resto delle opzioni di default.
  3. Dopo l'installazione, riavvia il PC.
  4. Verifica l'installazione:
      - Apri il terminale.
      - Digita il comando:
      ```bash
      git --version
      ```
      Dovresti vedere una risposta simile a:
      ```bash
      git version 2.x.x
      ```
      (Il numero della versione dipende da quella che hai installato.)

#### **Installare Visual Studio Code**
1. Scarica l'installer da [code.visualstudio.com](https://code.visualstudio.com/).
2. Installa VS Code seguendo le istruzioni.
3. Installa l’estensione **Python**:
   - Apri VS Code.
   - Vai su **Extensions** (icona dei 4 quadrati).
   - Cerca **Python** e installala.
4. Configura l’interprete Python:
   - Apri un file `.py` nel tuo progetto.
   - In basso a destra, clicca su **Select Interpreter** e scegli l’interprete Python installato.

### 2. **Predisporre ambiente di sviluppo**
1. Vai sulla pagina della repository su GitHub.
2. Clicca su **Code** > copia il link HTTPS.
3. Apri Visual Studio Code e apri il terminale (**Ctrl+ò**).
4. Clona la repository nel percorso desiderato:
    
    ```bash
    git clone https://github.com/utente/repo
    
    ```
5. **File > Open Folder** e seleziona la cartella dove è stata clonata la repository.

### 3. **Sincronizzare il codice**
**Pull**:
- Vai sui **tre puntini** in alto a destra nella sezione **Source Control**.
- Seleziona **Pull**.

Se desideri che VS Code chieda automaticamente di sincronizzare i cambiamenti:

1. Vai su **File > Preferences > Settings**.
2. Cerca **Git: Autofetch**.
3. Attiva l'opzione. Così, VS Code controllerà regolarmente gli aggiornamenti remoti.

### 4. **Variabili d'ambiente**
Aggiungere le variabili d'ambiente per Poppler e Google Vision OCR.

Scarica Poppler e configura variabile d'ambiente.
  1. Scarica **Poppler** da [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows).
  2. Estrai i file e aggiungi il percorso della cartella `bin` alle variabili d'ambiente in `PATH`.

Imposta una variabile d'ambiente per **Google Vision**.
  1. Aggiungi una variabile d'ambiente di sistema con:
      - **name**: `GOOGLE_APPLICATION_CREDENTIALS`
      - **value**: percorso/al/file/`google_credentials.json`

### 5. **Installare le dipendenze**
1. Vai nella cartella della repository:
   ```bash
   cd percorso-della-tua-repo
   ```
2. Crea e attiva l’ambiente virtuale (opzionale):
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3. Installa le dipendenze
    ```bash
    pip install -r requirements.txt
    ```

### 6. **Configurare il file `.env`**
Crea un file **.env** nella repo e aggiungi i seguenti valori:
```env
PDF_FOLDER=percorso/alla/cartella/pdf
EXCEL_PATH=percorso/al/file/excel
DATABASE_PATH=percorso/al/database/corsi
API_KEY=chiave_api_openai
POPPLER_PATH=percorso/alla/cartella/poppler/bin
GOOGLE_APPLICATION_CREDENTIALS=percorso/al/file/google_credentials.json
```
- **PDF_FOLDER**: è il percorso alla cartella dove inserire gli attestati da analizzare
- **EXCEL_PATH**: è il percorso al file Excel in cui scrivere i dati degli attestati analizzati
- **DATABASE_PATH**: è il percorso al file Excel dei corsi
- **API_KEY**: chiave OpenAI API
- **POPPLER_PATH**: percorso alla cartella `bin` di Poppler
- **GOOGLE_APPLICATION_CREDENTIALS**: percorso alla chiave JSON di Google Vision

### 7. **Esecuzione**
Esegui il programma principale con:
```bash
python attestati.py
```

## **🤝 Contributi**
Se vuoi contribuire a questo progetto, sentiti libero di:
- Aprire una **pull request** per aggiungere nuove funzionalità o migliorare quelle esistenti.
- Segnalare problemi nella sezione **Issues** della repository.

import io
import os
from utils.style import *
from pdf2image import convert_from_path
from utils.config import poppler_path, google_vision_path
from google.cloud import vision

# inizializza il client Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_vision_path
client = vision.ImageAnnotatorClient()

# Cloud Vision API 
def estrai_google_vision(pdf_path):
    """
    Estrae testo da un PDF multipagina utilizzando Google Vision OCR.
    """
    try:
        # converto pdf in img per google_vision
        immagini = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)

        # estrae testo per ogni img del pdf
        testo_completo = ""
        for img in immagini:
            # converte in byte
            img_byte_array = io.BytesIO()
            img.save(img_byte_array, format='PNG')
            img_content = img_byte_array.getvalue()

            image = vision.Image(content=img_content)
            response = client.text_detection(image=image)

            if response.error.message:
                raise Exception(f"Errore nell'API di Vision: {response.error.message}")

            testo_completo += response.text_annotations[0].description + "\n"
        return testo_completo.strip()

    except Exception as e:
        file_name = os.path.basename(pdf_path)
        print(f"\n{RED}Errore durante l'elaborazione del file {file_name} con Google Vision: {e}{RESET}")
        return "Errore"
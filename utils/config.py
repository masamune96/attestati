import os
from dotenv import load_dotenv

load_dotenv()

pdf_folder = os.getenv("PDF_FOLDER")
database_path = os.getenv("DATABASE_PATH")
excel_path = os.getenv("EXCEL_PATH")
openai_api_key = os.getenv("API_KEY")

# OCR config
poppler_path = os.getenv("POPPLER_PATH")
google_vision_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
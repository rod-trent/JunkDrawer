from pypdf import PdfReader
import re

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    # Clean up
    text = re.sub(r'\s+', ' ', text).strip()
    return text
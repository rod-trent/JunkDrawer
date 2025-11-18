import json
from .grok_client import grok_chat

def extract_text_from_pdf(pdf_file):
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text[:100000]  # limit to avoid huge payloads

def generate_flashcards(content, num_cards=30):
    prompt = f"""
You are an expert flashcard creator. Generate exactly {num_cards} high-quality Anki-style flashcards from the following text.
Focus on the most important concepts, definitions, processes, formulas, dates, etc.

Output ONLY a valid JSON array of objects with this exact structure:
[
  {{"front": "Question or term", "back": "Answer or definition"}},
  ...
]

Text:
{content}
"""
    messages = [{"role": "user", "content": prompt}]
    raw = grok_chat(messages, temperature=0.5)
    try:
        cards = json.loads(raw.strip("```json\n").strip("```"))
        return cards
    except:
        # fallback parsing
        start = raw.find("[")
        end = raw.rfind("]") + 1
        cards = json.loads(raw[start:end])
        return cards
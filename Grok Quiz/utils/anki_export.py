import genanki
import tempfile
import os

def export_to_anki(deck_name, flashcards):
    my_model = genanki.Model(
        1607392319,
        'Simple Model (Grok)',
        fields=[{'name': 'Front'}, {'name': 'Back'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
        }])

    my_deck = genanki.Deck(2059400110, deck_name)

    for i, card in enumerate(flashcards):
        note = genanki.Note(model=my_model, fields=[card["front"], card["back"]])
        my_deck.add_note(note)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".apkg") as f:
        genanki.Package(my_deck).write_to_file(f.name)
        return f.name
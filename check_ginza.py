import spacy
import sys

GINZA_UNAVAILABLE = False
try:
    nlp = spacy.load("ja_ginza")
    doc = nlp("これはテストです。犬は可愛い。")
    concepts = {token.lemma_ for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ"]}
    print(f"GiNZA loaded and processed text. Extracted concepts: {concepts}")
    if not concepts:
        print("Warning: GiNZA extracted no concepts. This might indicate a problem.")
        sys.exit(1)
except (OSError, ImportError) as e:
    print(f"Error: GiNZA model not found or not working correctly: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during GiNZA check: {e}")
    sys.exit(1)

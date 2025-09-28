# Handles dictionary lookups and translation services.
import os
import sudachipy
from sudachipy import tokenizer
from sudachipy import dictionary
import MeCab
import unidic_lite
import argostranslate.package
import argostranslate.translate
from .database_handler import DatabaseHandler

class DictionaryService:
    """Provides a unified interface for dictionary and translation services."""

    def __init__(self, db_path: str = "data/ejdict.sqlite3"):
        """Initializes the dictionary services."""
        self.sudachi_tokenizer = self._setup_sudachi()
        self.mecab_tokenizer = self._setup_mecab()
        self.ejdict_handler = DatabaseHandler(db_path)
        self._setup_argos()
        self.en_translator = self._get_en_translator()

    def _setup_sudachi(self):
        """Initializes the Sudachi tokenizer."""
        try:
            return dictionary.Dictionary().create()
        except Exception as e:
            print(f"Error initializing Sudachi: {e}")
            return None

    def _setup_mecab(self):
        """Initializes the MeCab tokenizer with UniDic."""
        try:
            return MeCab.Tagger(f"-d {unidic_lite.DICDIR}")
        except Exception as e:
            print(f"Error initializing MeCab: {e}")
            return None

    def _setup_argos(self):
        """Downloads and installs Argos Translate language packages if not present."""
        try:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # Install English package for EN->EN paraphrasing/definitions
            package_to_install = next(
                filter(
                    lambda x: x.from_code == "en" and x.to_code == "en",
                    available_packages,
                )
            )
            if not package_to_install.is_installed():
                 print("Downloading and installing Argos Translate English package...")
                 package_to_install.install()
        except Exception as e:
            print(f"Error during Argos Translate setup: {e}")

    def _get_en_translator(self):
        try:
            installed_langs = argostranslate.translate.get_installed_languages()
            en_lang = next(filter(lambda x: x.code == 'en', installed_langs))
            return en_lang.get_translation(en_lang)
        except StopIteration:
            print("Argos Translate English package not found.")
            return None
        except Exception as e:
            print(f"Error getting Argos EN translator: {e}")
            return None

    def tokenize_japanese_text_sudachi(self, text: str, mode: str = 'A'):
        if not self.sudachi_tokenizer:
            return None
        sudachi_mode = getattr(tokenizer.Tokenizer.SplitMode, mode, tokenizer.Tokenizer.SplitMode.A)
        return self.sudachi_tokenizer.tokenize(text, sudachi_mode)

    def tokenize_japanese_text_mecab(self, text: str):
        if not self.mecab_tokenizer:
            return None
        return self.mecab_tokenizer.parseToNode(text)

    def lookup_english_word(self, word: str) -> list[tuple]:
        return self.ejdict_handler.lookup_word(word)

    def translate_en_to_en(self, text: str) -> str | None: 
        """Translates English text to English, effectively paraphrasing."""
        if not self.en_translator:
            print("Argos EN->EN translator not available.")
            return None
        return self.en_translator.translate(text)

    def close(self):
        """Closes any open connections, like the database handler."""
        self.ejdict_handler.close()

# Example usage:
if __name__ == '__main__':
    service = DictionaryService()
    text = "日本語の形態素解析は難しい。"
    print(f"Tokenizing: {text}")
    
    print("\n--- SudachiPy ---")
    if service.sudachi_tokenizer:
        for m in service.tokenize_japanese_text_sudachi(text):
            print(f"{m.surface()}\t{m.part_of_speech()}")

    print("\n--- MeCab (UniDic) ---")
    if service.mecab_tokenizer:
        node = service.tokenize_japanese_text_mecab(text)
        while node:
            if node.surface:
                print(f"{node.surface()}\t{node.feature}")
            node = node.next

    print("\n--- EJDict-hand (SQLite) ---")
    if service.ejdict_handler.connection:
        word_to_lookup = "persistent"
        print(f"Looking up word: '{word_to_lookup}'")
        search_results = service.lookup_english_word(word_to_lookup)
        if search_results:
            for row in search_results:
                print(f"  Word: {row[0]}\n  Meaning: {row[1]}")
        else:
            print("Word not found.")

    print("\n--- Argos Translate (EN->EN) ---")
    if service.en_translator:
        text_to_translate = "Argos Translate is an offline translation library."
        print(f"Original: {text_to_translate}")
        translated_text = service.translate_en_to_en(text_to_translate)
        print(f"Translated (Paraphrased): {translated_text}")

    service.close()
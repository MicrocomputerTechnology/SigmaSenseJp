import sys
import os
import argparse

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pocket_library.dictionary_service import DictionaryService
from src.pocket_library.specialized_vocabulary_service import SpecializedVocabularyService

def analyze_sentence(sentence: str):
    """
    Analyzes a Japanese sentence, extracts key terms, and looks up their definitions
    across multiple specialized dictionaries.
    """
    import re
    print(f"--- Analyzing Sentence: \"{sentence}\" ---")

    dict_service = None
    spec_service = None
    results = {}

    try:
        # 1. サービスの準備
        print("Initializing services...")
        dict_service = DictionaryService()
        spec_service = SpecializedVocabularyService()
        print("Services initialized.")

        # 2. 括弧内の英語を優先検索
        print("Searching for English terms in parentheses...")
        parenthesized_terms = re.findall(r'[（\(](.*?)[）\)]', sentence)
        for term in parenthesized_terms:
            term = term.strip()
            if not term or not term.isascii(): continue

            term_results = []
            # Python用語辞書
            py_defs = spec_service.lookup_python_term(term)
            if py_defs:
                term_results.append(("Python", [d[1] for d in py_defs]))

            # 哲学用語辞書
            ph_defs = spec_service.lookup_philosophy_term(term)
            if ph_defs:
                term_results.append(("Philosophy", [d[1] for d in ph_defs]))

            if term_results:
                if term not in results:
                    results[term] = {"pos": "Parenthesized Term", "definitions": []}
                results[term]["definitions"].extend(term_results)

        # 3. 文章解析（サフィールの役割）
        print("Tokenizing sentence...")
        tokens = dict_service.tokenize_japanese_text_sudachi(sentence)
        if not tokens:
            print("Could not tokenize the sentence.")
            return

        key_pos = {"名詞", "動詞", "形容詞"} # 注目する品詞 (Nouns, Verbs, Adjectives)

        # 4. 横断的な辞書検索
        print("Looking up key terms...")
        for token in tokens:
            surface = token.surface()
            part_of_speech = token.part_of_speech()[0]
            lemma = token.normalized_form() # 基本形 (e.g., 走る for 走った)

            # 括弧とその中身はスキップ
            if surface in '()（）' or surface in parenthesized_terms:
                continue

            if part_of_speech in key_pos:
                term_results = []
                
                # Python用語辞書
                py_defs = spec_service.lookup_python_term(lemma)
                if py_defs:
                    term_results.append(("Python", [d[1] for d in py_defs]))

                # 哲学用語辞書
                ph_defs = spec_service.lookup_philosophy_term(lemma)
                if ph_defs:
                    term_results.append(("Philosophy", [d[1] for d in ph_defs]))

                # 英和辞書 (英語のまま検索)
                en_defs = dict_service.lookup_english_word(surface)
                if en_defs:
                    term_results.append(("E-J Dictionary", [d[1] for d in en_defs]))

                if term_results:
                    if lemma not in results:
                        results[lemma] = {"pos": part_of_speech, "definitions": []}
                    results[lemma]["definitions"].extend(term_results)

        # 5. 結果の提示
        print("\n--- Analysis Report ---")
        if not results:
            print("No definitions found for key terms in the sentence.")
            return

        for term, data in results.items():
            print(f"\n■ Term: {term} (Part of Speech: {data['pos']})")
            for source, defs in data['definitions']:
                print(f"  ● From: {source}")
                for definition in defs:
                    print(f"    - {definition}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 6. サービスを閉じる
        if dict_service:
            dict_service.close()
        if spec_service:
            spec_service.close()
        print("\n--- Analysis Complete ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze a Japanese sentence and look up definitions of its key terms.')
    parser.add_argument('sentence', type=str, help='The Japanese sentence to analyze.')
    args = parser.parse_args()

    analyze_sentence(args.sentence)

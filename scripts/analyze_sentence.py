import sys
import os
import argparse
import json

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pocket_library.dictionary_service import DictionaryService
from src.pocket_library.specialized_vocabulary_service import SpecializedVocabularyService
from src.world_model import WorldModel
from src.symbolic_reasoner import SymbolicReasoner
from src.gemini_client import GeminiClient

def analyze_sentence(sentence: str):
    """
    Analyzes a Japanese sentence, checks for logical consistency, and generates a correction if needed.
    """
    import re
    print(f"--- Analyzing Sentence: \"{sentence}\" ---")

    dict_service = None
    spec_service = None
    results = {}
    key_lemmas = []

    try:
        # 1. サービスの準備
        print("Initializing services...")
        dict_service = DictionaryService()
        spec_service = SpecializedVocabularyService()
        wm = WorldModel()
        reasoner = SymbolicReasoner(world_model=wm)

        # --- For Demonstration: Add knowledge programmatically ---
        # In a real application, this knowledge would be in world_model.json
        print("Injecting temporary knowledge for demonstration...")
        wm.add_node('団子', name_ja="団子")
        wm.add_node('和菓子', name_ja="和菓子")
        wm.add_node('食べ物', name_ja="食べ物")
        wm.add_node('重し', name_ja="重し")
        wm.add_node('物体', name_ja="物体")
        wm.add_edge('団子', '和菓子', 'is_a')
        wm.add_edge('和菓子', '食べ物', 'is_a')
        wm.add_edge('重し', '物体', 'is_a')
        # -----------------------------------------------------

        print("Services initialized.")

        # (省略) ... 辞書検索までの処理は同じ ...
        print("Searching for English terms in parentheses...")
        parenthesized_terms = re.findall(r'[（\(](.*?)[）\)]', sentence)
        for term in parenthesized_terms:
            term = term.strip()
            if not term or not term.isascii(): continue
            if term not in key_lemmas:
                key_lemmas.append(term)

        print("Tokenizing sentence...")
        tokens = dict_service.tokenize_japanese_text_sudachi(sentence)
        if not tokens:
            print("Could not tokenize the sentence.")
            return

        key_pos = {"名詞"}
        for token in tokens:
            lemma = token.normalized_form()
            if token.part_of_speech()[0] in key_pos:
                if lemma not in key_lemmas and lemma not in '()（）':
                    key_lemmas.append(lemma)

        # 5. 論理的矛盾の検出
        print("\n--- Checking for Logical Consistency ---")
        print(f"Key terms for reasoning: {key_lemmas}")
        consistency_result = reasoner.check_category_consistency(key_lemmas)
        
        if not consistency_result['consistent']:
            print("\n[! ] Logical Contradiction Detected!")
            print(f"    Reason: {consistency_result['reason']}")
            
            # 6. LLMによる修正案の生成
            print("\n--- Generating Correction with Orient (LLM) ---")
            try:
                gemini_client = GeminiClient()
                violator = consistency_result['violator']
                expected_category = consistency_result['context_category']

                prompt = f"""あなたは、知的で親切なアシスタントです。
ユーザーが入力した文章に、論理的な誤りが見つかりました。
その誤りを優しく指摘し、文脈に沿った適切な代替案を提案してください。

元の文章: 「{sentence}」

検出された論理エラー:
- 文脈のカテゴリ: 「{expected_category}」
- カテゴリに属さない項目: 「{violator}」

応答は、例えば「〇〇は△△ではないようです。××ではありませんか？」のような、自然な対話形式で、日本語でお願いします。"""

                print("Querying LLM for a suggestion...")
                correction = gemini_client.query_text(prompt)

                print("\n--- Smart Correction ---")
                print(f"> {correction}")

            except Exception as e:
                print(f"Could not generate correction: {e}")

        else:
            print("No logical contradictions detected.")

        # (省略) ... 辞書検索結果の表示 ...

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # サービスを閉じる
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

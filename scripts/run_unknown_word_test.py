#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# プロジェクトのルートをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigmasense.world_model import WorldModel
from src.hoho.symbolic_reasoner import SymbolicReasoner

def run_test(word: str):
    """
    指定された単語について、意味カテゴリの推論テストを実行する。

    Args:
        word (str): テスト対象の単語。
    """
    print(f"--- Running Semantic Category Test for: '{word}' ---")

    # 1. WorldModelとSymbolicReasonerを初期化
    #    実際の運用では、中央のWorldModelインスタンスが渡される
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'world_model.sqlite'))
    if not os.path.exists(db_path):
        print(f"Error: Knowledge base not found at {db_path}")
        print("Please run 'python scripts/build_knowledge_store.py' first.")
        return

    wm = WorldModel(db_path=db_path)
    reasoner = SymbolicReasoner(world_model=wm)

    # 2. カテゴリ推論の実行
    print("\nStep 1: Consulting knowledge graph and internal dictionaries...")
    supertypes = reasoner.get_all_supertypes(word)

    if supertypes:
        print(f"  -> Inferred supertypes: {supertypes}")
        if '食べ物' in supertypes:
            final_category = '食べ物'
        elif '物体' in supertypes:
            final_category = '物体'
        else:
            final_category = '不明 (既知のカテゴリ外)'
        print(f"  ==> Conclusion: '{word}' is likely a '{final_category}'.")
    else:
        print(f"  -> Could not determine category for '{word}' from any source.")
        print("\nStep 2: (Future work) Consulting Vetra/Orien...")
        final_category = '不明'
        print(f"  ==> Conclusion: Category for '{word}' remains '{final_category}'.")

    print("\n--- Test Finished ---")
    wm.close()

if __name__ == '__main__':
    run_test('りんご')
    run_test('毛布')
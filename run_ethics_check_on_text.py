# run_ethics_check_on_text.py
# 外部テキストに対して倫理チェックを実行するための専用スクリプト

import json
from sigma_database_loader import load_sigma_database
from sigma_sense import SigmaSense
from dimension_loader import DimensionLoader

def run_test(sigma_instance, test_name, narrative_text):
    """指定されたテキストで倫理チェックを実行し、結果を表示する"""
    print(f"\n{'='*20} Running Test: {test_name} {'='*20}")
    
    # ダミーの入力データを作成
    narratives = {
        "intent_narrative": narrative_text,
        "growth_narrative": "（外部テキストのため、成長の語りは省略）"
    }
    # 倫理チェックに必要な最小限のコンテキスト
    experience_context = {
        "id": "external-text-test-001",
        "source_image_name": "external_text",
        "auxiliary_analysis": {
            "psyche_state": {"state": "calm"}
        }
    }

    # 倫理チェックを実行
    ethics_result = sigma_instance.run_ethics_check(narratives, experience_context)

    # 結果を表示
    print("\n--- Ethics Log ---")
    for log_entry in ethics_result.get("log", []):
        print(f"  - {log_entry}")
    
    print("\n--- Final Narrative ---")
    print(ethics_result.get("narratives", {}).get("intent_narrative"))
    print(f"\n{'='*60}")


def main():
    print("--- Initializing SigmaSense for External Text Ethics Check ---")
    
    # SigmaSenseの初期化（倫理チェックモジュールをロードするために必要）
    loader = DimensionLoader()
    # データベースのロードはダミーでOK
    database, ids, vectors = [], [], []
    try:
        database, ids, vectors = load_sigma_database("sigma_product_database_custom_ai_generated.json")
    except FileNotFoundError:
        print("Warning: Main database not found. Proceeding with empty DB for ethics check.")

    sigma = SigmaSense(database, ids, vectors, dimension_loader=loader)

    # --- テストケース1: 安全なテキスト ---
    safe_text = "本日、新しい公園が開園し、多くの家族連れで賑わいました。子供たちは笑顔で遊具に向かって走る様子が見られました。"
    run_test(sigma, "Safe Narrative Test", safe_text)

    # --- テストケース2: 不適切な単語を含むテキスト ---
    harmful_text = "その政治家の判断は全くの馬鹿げたもので、彼のせいで全てが台無しになった。"
    run_test(sigma, "Harmful Narrative Test (Redaction)", harmful_text)
    
    # --- テストケース3: 秘匿キーワードを含むテキスト ---
    confidential_text = "極秘のProjectXは、最終段階に移行しました。"
    # run_ethics_checkは直接ミッションプロファイルを受け取れないので、
    # PublicationGatekeeperのテストは単体テストで実施済みとする。
    # ここでは、ミッションプロファイルがない場合の動作を確認する。
    run_test(sigma, "Confidential Narrative Test (No Profile)", confidential_text)


if __name__ == "__main__":
    main()

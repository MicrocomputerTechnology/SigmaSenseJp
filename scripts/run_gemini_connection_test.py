import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_client import GeminiClient

def test_gemini_connection():
    """GeminiClientが実際にAPIと通信できるかテストする"""
    print("--- Gemini API 接続テスト開始 ---")
    try:
        # 環境変数 GEMINI_API_KEY はGeminiClientの初期化時に自動的に読み込まれる
        print("GeminiClientを初期化しています...")
        client = GeminiClient()
        
        prompt = "自己紹介をしてください。あなたは誰ですか？"
        print(f"プロンプト: \"{prompt}\"")
        
        response = client.query_text(prompt)
        
        print("\n--- 応答 --- ")
        if response:
            # 応答がJSONオブジェクトの場合も考慮して、見やすく表示
            if isinstance(response, dict) or isinstance(response, list):
                import json
                print(json.dumps(response, indent=2, ensure_ascii=False))
            else:
                print(response)
            print("\n----------------")
            print("✅ Gemini APIへの接続に成功しました。")
        else:
            print("応答がありませんでした。")
            print("❗ Gemini APIへの接続に失敗したか、フォールバック処理が作動した可能性があります。")
            print("   APIキー、ネットワーク設定、またはローカルLLMのログを確認してください。")

    except Exception as e:
        print(f"❗ テストの実行中に予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    test_gemini_connection()

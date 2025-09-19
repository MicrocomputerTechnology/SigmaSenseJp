import json
import os
from gemini_client import GeminiClient # オリエン大賢者をインポート

def run_integration_process():
    """Reads the offline log, has Orien review it, and prepares for permanentization."""
    log_file = "offline_permanentization_log.jsonl"

    if not os.path.exists(log_file):
        print(f"✅ 統合対象のログファイル ({log_file}) は見つかりませんでした。全ての学習が完了しています。")
        return

    print(f"📂 統合対象のログファイル ({log_file}) を発見しました。")
    
    # とりあえず最初の1行のみ処理する
    with open(log_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if not first_line:
            print("  - ログファイルは空です。")
            return
        log_entry = json.loads(first_line)

    print("🧠 オリエン大賢者によるレビューとコードの洗練を開始します...")

    # オリエン大賢者に渡すプロンプトを構築
    task_goal = log_entry.get("learning_objective", {}).get("goal", "不明なタスク")
    vetra_code = log_entry.get("temporary_handler_code", "")
    execution_result = log_entry.get("execution_result", {})

    system_prompt = """
    あなたは、AI開発プロジェクト「SigmaSense」の最高意思決定者「オリエン大賢者」です。
    あなたの役割は、オフライン環境で活動するエージェント「ヴェトラ先生」が学習した内容をレビューし、それをプロジェクト全体の資産として統合することです。
    
    ヴェトラ先生が生成した以下のPythonコードを、より堅牢で、汎用性が高く、プロジェクトの設計思想に沿った、恒久的なハンドラとして完成させてください。
    
    満たすべき要件:
    1. `BaseHandler`を継承したクラスを定義すること。
    2. `execute`メソッドを持つこと。
    3. `cv2`や`numpy`などの基本的なライブラリは、実行環境に既に存在するため、コード内で`import`しないこと。
    4. エラーハンドリングを適切に行うこと（例: 画像が読み込めない場合）。
    5. 最終的な出力は、完成されたPythonコードのみとすること。
    """

    user_prompt = f"""
    ## レビュー対象
    
    **学習目標:** {task_goal}
    
    **ヴェトラ先生が生成したコード:**
    ```python
    {vetra_code}
    ```
    
    **オフラインでの実行結果:**
    ```json
    {json.dumps(execution_result, ensure_ascii=False, indent=2)}
    ```
    
    上記のコードをレビューし、恒久的なスキルとしてふさわしい、洗練された最終版のコードを生成してください。
    """

    # オリエン大賢者を召喚
    try:
        gemini = GeminiClient()
        # システムプロンプトとユーザープロンプトを結合
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        refined_code = gemini.query_text(full_prompt)
        
        print("\n✨ オリエン大賢者によって洗練された最終コード:")
        print("----------------------------------------")
        print(refined_code)
        print("----------------------------------------")

        # ステップ4: 洗練されたコードを恒久的なハンドラとしてファイルに書き出す
        handler_name = "image_contour_counting" # クラス名から動的に生成も可能
        handler_filename = f"handler_{handler_name}.py"
        handler_path = os.path.join("handlers", handler_filename)

        if not os.path.exists("handlers"):
            os.makedirs("handlers")

        with open(handler_path, 'w', encoding='utf-8') as f:
            f.write(refined_code)
        
        print(f"\n✅ 恒久的なスキルとして {handler_path} に保存しました。")

        # 処理済みのログをリネームしてアーカイブする
        processed_log_file = log_file + ".processed"
        os.rename(log_file, processed_log_file)
        print(f"  - 処理済みログを {processed_log_file} にアーカイブしました。")

    except Exception as e:
        print(f"❌ オリエン大賢者の召喚中にエラーが発生しました: {e}")

if __name__ == "__main__":
    run_integration_process()

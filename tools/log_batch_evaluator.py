import sys
import os
import sys
import os

# スクリプトのディレクトリからプロジェクトのルートディレクトリを特定し、sys.pathに追加
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
from evaluation_template import display_result
from response_logger import ResponseLogger

# ログファイルのパス
LOG_DIR = "sigma_logs"

def evaluate_logs():
    print("🚀 ログファイルの評価を開始します。")
    
    log_files = [f for f in os.listdir(LOG_DIR) if f.startswith("sigma_log_") and f.endswith(".jsonl")]
    if not log_files:
        print("❗ 評価対象のログファイルが見つかりません。")
        return

    for log_file in sorted(log_files):
        log_path = os.path.join(LOG_DIR, log_file)
        print(f"\n--- {log_file} の評価 --- ")
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        result = json.loads(line.strip())
                        display_result(result)
                        print("-" * 70)
                    except json.JSONDecodeError:
                        print(f"❗ 無効なJSON形式の行をスキップしました: {line.strip()}")
        except Exception as e:
            print(f"❗ ログファイルの読み込み中にエラーが発生しました: {e}")

    print("\n✅ ログファイルの評価が完了しました。")

if __name__ == "__main__":
    evaluate_logs()

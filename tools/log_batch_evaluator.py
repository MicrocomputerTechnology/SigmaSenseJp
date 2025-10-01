import sys
import os
import json

# スクリプトのディレクトリからプロジェクトのルートディレクトリを特定し、sys.pathに追加
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root, 'src'))

from sigmasense.evaluation_template import display_result
from vetra.vetra_llm_core import VetraLLMCore
from sigmasense.sigma_sense import SigmaSense
from sigmasense.sigma_database_loader import load_sigma_database
from sigmasense.dimension_loader import DimensionLoader

# ログファイルのパス
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

LOG_DIR = os.path.join(project_root, "sigma_logs")

def evaluate_logs():
    print("🚀 ログファイルの評価を開始します。")

    # DimensionLoaderを一度だけ初期化
    try:
        loader = DimensionLoader()
    except Exception as e:
        print(f"❗ DimensionLoaderの初期化に失敗しました: {e}")
        return

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
                        # loaderを引数として渡す
                        display_result(result, loader)
                        print("-" * 70)
                    except json.JSONDecodeError:
                        print(f"❗ 無効なJSON形式の行をスキップしました: {line.strip()}")
        except Exception as e:
            print(f"❗ ログファイルの読み込み中にエラーが発生しました: {e}")

    print("\n✅ ログファイルの評価が完了しました。")

def main():
    db_path = os.path.join(project_root, "data", "world_model.sqlite")

if __name__ == "__main__":
    evaluate_logs()
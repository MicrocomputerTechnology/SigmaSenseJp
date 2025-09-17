import json
import os
from datetime import datetime

class ResponseLogger:
    """
    SigmaSenseの照合結果をJSON Lines形式でファイルに記録するロガー。
    """
    def __init__(self, log_dir="sigma_logs"):
        """
        ロガーを初期化し、ログファイルのパスを準備する。
        ログファイル名は実行日時から自動的に生成される。
        """
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(log_dir, f"sigma_log_{timestamp}.jsonl")
        self._initialized = True
        print(f"📝 ログファイルを準備しました: {self.log_path}")

    def log(self, result_data):
        """
        単一の照合結果を辞書として受け取り、JSON文字列としてファイルに追記する。
        
        Args:
            result_data (dict): sigma_sense.match()から返される結果の辞書。
        """
        if not self._initialized:
            print("❗エラー: ロガーが初期化されていません。")
            return

        try:
            # ファイルに追記モードで書き込む
            with open(self.log_path, 'a', encoding='utf-8') as f:
                # 辞書をJSON文字列に変換して書き込む（改行付き）
                f.write(json.dumps(result_data, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"❗ログの書き込み中にエラーが発生しました: {e}")

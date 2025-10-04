import json
import os
import numpy as np

from typing import Optional

class CorrectionApplicator:
    def __init__(self, config: Optional[dict] = None, failure_log_path: Optional[str] = None):
        if config is None:
            config = {}

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        log_dir = os.path.join(project_root, "sigma_logs")

        self.failure_log_path = failure_log_path or os.path.join(log_dir, "functor_consistency_failures.jsonl")

        # Load strategy and parameters from config
        self.strategy = config.get("strategy", "multiplicative")
        self.alpha = config.get("alpha", 0.5)
        
        self.failure_logs = self._load_failure_logs(self.failure_log_path)
        if self.failure_logs:
            print(f"🌿 CorrectionApplicatorが {len(self.failure_logs)}件の補正ルールで初期化されました。")
            print(f"   - 戦略: {self.strategy}, Alpha: {self.alpha}")

    def _load_failure_logs(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f]
        except (IOError, json.JSONDecodeError) as e:
            print(f"❗ 補正ルールの読み込みエラー: {e}")
            return []

    def apply_to_vector(self, vector, image_id):
        """単一のベクトルに補正を適用する"""
        if not self.failure_logs:
            return vector

        corrected_vector = np.array(vector, dtype=np.float32)

        for log in self.failure_logs:
            log_image_id = os.path.splitext(log.get('image', ''))[0]
            if image_id != log_image_id:
                continue

            changed_indices = set(log.get('changed_indices', []))
            expected_indices = set(log.get('expected_indices', []))
            unexpected_indices = list(changed_indices - expected_indices)
            vector_diff = np.array(log.get('vector_diff', []))

            for i in unexpected_indices:
                if i < len(vector_diff):
                    diff = vector_diff[i]
                    attenuation = diff * self.alpha
                    original_value = corrected_vector[i]

                    if self.strategy == 'multiplicative':
                        corrected_value = original_value * (1 - attenuation)
                    elif self.strategy == 'subtractive':
                        corrected_value = original_value - attenuation
                    else: # Default to multiplicative if strategy is unknown
                        corrected_value = original_value * (1 - attenuation)

                    corrected_vector[i] = max(0.0, corrected_value)
        
        return corrected_vector

    def apply_to_database(self, db_data):
        """データベース全体（辞書のリスト）に補正を適用する"""
        if not self.failure_logs:
            print("✅ 補正ルールはありませんでした。データベースは既に安定的です。")
            return db_data

        print(f"📝 {len(self.failure_logs)}件の補正ルールに基づき、データベース全体を補正します。")
        
        # 扱いやすいようにIDをキーにした辞書に変換
        db_dict = {item['id']: item for item in db_data}

        for log in self.failure_logs:
            image_name = log.get('image')
            if not image_name:
                continue

            item_id = os.path.splitext(image_name)[0]

            if item_id in db_dict:
                original_vector = np.array(db_dict[item_id]['meaning_vector'])
                corrected_vector = self.apply_to_vector(original_vector, item_id)
                db_dict[item_id]['meaning_vector'] = corrected_vector
                print(f"  🔧 ID '{item_id}' のベクトルを補正しました。")

        return list(db_dict.values())

import os
import json
import numpy as np
from src.config_loader import ConfigLoader
from dimension_loader import DimensionLoader

# DimensionLoaderのインスタンスを生成
loader = DimensionLoader()

def map_critical_structure(config: dict, log_dir="sigma_logs"):
    """
    照合不能群のログを抽出し、その平均ベクトル（臨界構造）を動的に計算する。
    """
    unmatchable_threshold = config.get("unmatchable_threshold", 0.6)
    unmatchable_vectors = []

    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith(".jsonl"):
            continue
        
        path = os.path.join(log_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log = json.loads(line)
                except json.JSONDecodeError:
                    continue

                score = log.get("best_match", {}).get("score", 0.0)
                if score < unmatchable_threshold:
                    vector = log.get("vector", [])
                    if len(vector) == loader.vector_size:
                        unmatchable_vectors.append(vector)

    if not unmatchable_vectors:
        return {
            "message": "No unmatchable group found.",
            "unmatchable_count": 0,
            "critical_vector": [0.0] * loader.vector_size,
            "critical_structure_named": {}
        }

    mean_vector = np.mean(unmatchable_vectors, axis=0)
    
    # 各次元の名前と平均値をマッピング
    critical_structure_named = {
        dim['id']: mean_vector[i]
        for i, dim in enumerate(loader.get_dimensions())
    }

    return {
        "unmatchable_count": len(unmatchable_vectors),
        "critical_vector_raw": mean_vector.tolist(),
        "critical_structure_named": critical_structure_named
    }

if __name__ == '__main__':
    # テスト実行用
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    config_loader = ConfigLoader(config_dir)
    cs_config = config_loader.get_config('critical_structure_mapper_profile')
    if not cs_config:
        print("Warning: critical_structure_mapper_profile.json not found. Using default threshold.")
        cs_config = {}

    report = map_critical_structure(cs_config)
    import pprint
    pprint.pprint(report)
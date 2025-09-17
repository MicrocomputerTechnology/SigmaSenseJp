import os
import json
import numpy as np
from dimension_loader import dimension_loader

# 照合不能と見なすスコアの閾値
UNMATCHABLE_THRESHOLD = 0.6

def map_critical_structure(log_dir="sigma_logs"):
    """
    照合不能群のログを抽出し、その平均ベクトル（臨界構造）を動的に計算する。
    """
    unmatchable_vectors = []

    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith(".json"):
            continue
        
        path = os.path.join(log_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                continue

        score = log.get("best_match", {}).get("score", 0.0)
        if score < UNMATCHABLE_THRESHOLD:
            vector = log.get("vector", [])
            if len(vector) == dimension_loader.vector_size:
                unmatchable_vectors.append(vector)

    if not unmatchable_vectors:
        return {
            "message": "No unmatchable group found.",
            "unmatchable_count": 0,
            "critical_vector": [0.0] * dimension_loader.vector_size,
            "critical_structure_named": {}
        }

    mean_vector = np.mean(unmatchable_vectors, axis=0)
    
    # 各次元の名前と平均値をマッピング
    critical_structure_named = {
        dim['id']: mean_vector[i]
        for i, dim in enumerate(dimension_loader.get_dimensions())
    }

    return {
        "unmatchable_count": len(unmatchable_vectors),
        "critical_vector_raw": mean_vector.tolist(),
        "critical_structure_named": critical_structure_named
    }

if __name__ == '__main__':
    # テスト実行用
    report = map_critical_structure()
    import pprint
    pprint.pprint(report)

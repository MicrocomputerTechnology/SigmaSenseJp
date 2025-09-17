import os
import json
import numpy as np
from dimension_loader import DimensionLoader

def aggregate_semantic_axes(log_dir="sigma_logs"):
    """
    ログファイルから全意味軸の平均値を動的に集計する。
    """
    # Instantiate a loader to get the dimension definitions
    loader = DimensionLoader(
        selia_path="vector_dimensions_custom_ai.json", 
        lyra_path="vector_dimensions_custom_ai_lyra.json"
    )
    dimension_ids = [dim['id'] for dim in loader.get_dimensions()]
    axes_data = {dim_id: [] for dim_id in dimension_ids}
    
    axes_data['score'] = []
    axes_data['entropy'] = []
    axes_data['sparsity'] = []

    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith(".jsonl"): # 修正点1: .jsonl に変更
            continue

        path = os.path.join(log_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f): # 修正点2: 各行を読み込む
                try:
                    log_data = json.loads(line) # 修正点3: 各行を個別にパース
                except json.JSONDecodeError:
                    print(f"Warning: Skipping corrupted or malformed JSON line in {fname} at line {line_num + 1}")
                    continue

                vector = log_data.get('vector', [])
                
                # ベクトルから各次元の値を取得
                for i, dim_id in enumerate(dimension_ids):
                    if i < len(vector):
                        axes_data[dim_id].append(vector[i])

                # その他のメトリクスを取得
                metrics = log_data.get('information_metrics', {})
                axes_data['entropy'].append(metrics.get('entropy', 0.0))
                axes_data['sparsity'].append(metrics.get('sparsity', 0.0))
                
                best_match = log_data.get('best_match', {})
                axes_data['score'].append(best_match.get('score', 0.0))

    aggregated_results = {}
    for key, values in axes_data.items():
        if values:
            aggregated_results[key] = np.mean(values)
        else:
            aggregated_results[key] = 0.0
            
    return aggregated_results

if __name__ == '__main__':
    # テスト実行用
    results = aggregate_semantic_axes()
    import pprint
    pprint.pprint(results)

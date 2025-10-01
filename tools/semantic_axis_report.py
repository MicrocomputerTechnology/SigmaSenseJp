import sys
import os
import numpy as np

# 親ディレクトリをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root, 'src'))

from saphiel.semantic_axis_aggregator import aggregate_semantic_axes

def generate_narrative(source_image_name, match_result, source_vector, target_vector, dimensions, hint=None, top_n=3):
    """
    個別の照合結果に基づいて、なぜ類似しているかを説明する「語り」を生成する。
    """
    if not match_result or not target_vector:
        return f"Aegis assessment: No meaningful similarities found for {source_image_name} to warrant a narrative."

    target_image_name = match_result['image_name']
    score = match_result['score']
    category = match_result['category']

    if score < 0.5: # ある程度の類似度がないと語れない
        return f"Aegis assessment: The similarity between {source_image_name} and {target_image_name} (Score: {score:.2f}) is too low to generate a detailed narrative."

    # 各次元の差を計算
    source_vec = np.array(source_vector)
    target_vec = np.array(target_vector)
    diff = np.abs(source_vec - target_vec)

    # 差が小さい（類似度が高い）次元のインデックスを取得
    dimension_ids = list(dimensions.keys())
    # np.argsort(diff) は昇順（小さい順）にソートしたインデックスを返す
    similar_dimension_indices = np.argsort(diff)[:top_n]

    # 類似している次元の名前を取得
    similar_dimension_names = []
    for i in similar_dimension_indices:
        dim_id = dimension_ids[i]
        dim_info = dimensions.get(dim_id)
        if dim_info and isinstance(dim_info, dict):
            similar_dimension_names.append(dim_info.get('name', f"Unnamed Dimension ID: {dim_id}"))
        else:
            similar_dimension_names.append(f"Unknown Dimension ID: {dim_id}")

    # 語りを生成
    narrative = (
        f"Analysis of similarity between '{source_image_name}' and '{target_image_name}':\n"
        f"  - Match Category: {category} (Score: {score:.3f})\n"
        f"  - This similarity is primarily based on the following shared characteristics:\n"
        f"    - {', '.join(similar_dimension_names)}"
    )

    # ヒントがあれば、それを前に追加する
    if hint and 'prompt_hint' in hint:
        narrative = f"[Narrative Hint]: {hint['prompt_hint']}\n\n{narrative}"

    return narrative


def generate_semantic_report():
    summary = aggregate_semantic_axes()
    print("\n🧠 意味空間照合軸の集約レポート")
    print("-" * 40)
    for k, v in summary.items():
        # キーを25文字に拡張し、値を小数点以下4桁でフォーマット
        print(f"{k:>25}: {v:.4f}")
    print("-" * 40)
    print("このレポートは、照合器がどの意味軸に強く依存しているか、")
    print("また照合不能群がどの軸で臨界構造を形成しているかを示します。")

if __name__ == "__main__":
    generate_semantic_report()

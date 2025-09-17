import os
import json
from collections import OrderedDict
from sigma_database_loader import load_sigma_database
from sigma_sense import SigmaSense
from response_logger import ResponseLogger
from evaluation_template import display_result
from dimension_loader import DimensionLoader
from tools.semantic_axis_report import generate_narrative
from aegis_ethics_filter import AegisEthicsFilter
from narrative_hint_generator import NarrativeHintGenerator
from fusion_mapper import FusionMapper

import numpy as np

def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# 実験対象画像ディレクトリと意味データベースのパス
IMG_DIR = "sigma_images"
DB_PATH = "sigma_product_database_custom_ai_generated.json"
AEGIS_PROFILE_PATH = "saphiel_mission_profile.json"
SELIA_DIMS_PATH = "vector_dimensions_custom_ai.json"
LYRA_DIMS_PATH = "vector_dimensions_custom_ai_lyra.json"


def is_image_file(fname):
    return fname.lower().endswith((".png", ".jpg", ".jpeg"))

def main():
    # イージスフィルターと次元定義の読み込み
    aegis = AegisEthicsFilter(AEGIS_PROFILE_PATH)
    hint_generator = NarrativeHintGenerator()
    
    # DimensionLoaderのインスタンス化
    loader = DimensionLoader(selia_path=SELIA_DIMS_PATH, lyra_path=LYRA_DIMS_PATH)
    dims_selia = loader._selia_dims
    dims_lyra = loader._lyra_dims
    
    # SeliaとLyraの次元を結合して全次元マップを作成
    dimensions_all = OrderedDict()
    for dim in dims_selia:
        dimensions_all[dim['id']] = dim
    for dim in dims_lyra:
        dimensions_all[dim['id']] = dim

    print("--- Starting SigmaSense Processing ---")
    
    # 意味データベースの読み込み
    database, ids, vectors = load_sigma_database(DB_PATH)

    # 照合器インスタンスの生成（次元ファイルのパスを明示的に渡す）
    sigma = SigmaSense(
        database,
        ids,
        vectors,
        selia_dims_path=SELIA_DIMS_PATH,
        lyra_dims_path=LYRA_DIMS_PATH
    )

    # 新しいロガーを初期化
    logger = ResponseLogger()

    # Create a directory for fusion maps if it doesn't exist
    fusion_map_dir = os.path.join(os.path.dirname(logger.log_path), "fusion_maps")
    os.makedirs(fusion_map_dir, exist_ok=True)

    # 対象画像群に対して照合処理を実行
    for fname in sorted(os.listdir(IMG_DIR)):
        if is_image_file(fname):
            img_path = os.path.join(IMG_DIR, fname)

            # 意味ベクトル生成 → 再構成判定 → 照合 → 応答生成
            result = sigma.match(img_path)

            # --- Fusion Map Generation ---
            if "fusion_data" in result and result["fusion_data"]:
                mapper = FusionMapper(result["fusion_data"])
                dot_string = mapper.generate_dot_graph()
                
                # Save the DOT file
                base_name = os.path.splitext(fname)[0]
                output_dot_path = os.path.join(fusion_map_dir, f"{base_name}_fusion_map.dot")
                with open(output_dot_path, 'w') as f:
                    f.write(dot_string)
                
                print(f"\n--- Fusion Map Generated ---")
                print(f"Saved to: {output_dot_path}")
                # Add this info to the result for logging
                result["fusion_map_path"] = output_dot_path
            # -----------------------------

            # 語り生成
            best_match = result.get("best_match")
            if best_match and best_match.get("image_name"):
                # 語り生成のため、best_match辞書にカテゴリ情報を追加
                best_match['category'] = result.get('response')
                
                # Generate narrative hint
                hint = hint_generator.generate_hint(
                    similarity_score=best_match.get('score', 0.0),
                    vec1=result.get("vector"),
                    vec2=best_match.get("vector")
                )
                result['narrative_hint'] = hint # Log the hint

                narrative = generate_narrative(
                    source_image_name=result.get("source_image_name"),
                    match_result=best_match,
                    source_vector=result.get("vector"),
                    target_vector=best_match.get("vector"),
                    dimensions=dimensions_all, # 常に全次元を渡す
                    hint=hint
                )
            else:
                narrative = f"No significant match found for {result.get('source_image_name')} to generate a narrative."

            # 倫理フィルター適用
            filtered_narrative, intervened = aegis.filter(
                narrative=narrative,
                image_name=result.get("source_image_name")
            )

            # 結果オブジェクトに語りと介入情報を追加
            result["narrative"] = filtered_narrative
            result["aegis_intervention"] = intervened

            # CLI表示
            display_result(result)

            # 語りと介入結果を表示
            print("\n--- Narrative Analysis ---")
            print(filtered_narrative)
            if intervened:
                print("\033[91m>>> AEGIS INTERVENTION RECORDED <<< [0m") # 赤色で表示

            # 新しいロガーで結果を記録
            cleaned_result = convert_numpy_types(result)
            logger.log(cleaned_result)
            print("-" * 70) # 区切り線

    print("\n✅ 全画像の処理が完了しました。")
    print(f"ログは {logger.log_path} に保存されています。")
    print(f"Fusion maps saved in {fusion_map_dir}")

if __name__ == "__main__":
    main()

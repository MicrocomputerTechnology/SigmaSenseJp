# === 第十六次実験 実行スクリプト ===

import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigma_database_loader import load_sigma_database
from src.sigma_sense import SigmaSense
from src.response_logger import ResponseLogger
from src.dimension_loader import DimensionLoader
import numpy as np

def convert_numpy_types(obj):
    """JSONシリアライズのためにNumpyの型をPythonネイティブ型に変換する"""
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

import argparse

# --- 定数定義 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def is_image_file(fname):
    return fname.lower().endswith((".png", ".jpg", ".jpeg"))

def display_unified_result(result):
    """第十六次実験の新しい結果オブジェクトを表示する"""
    print(f"\n{'='*20} Result for: {result.get('source_image_name', 'N/A')} {'='*20}")
    
    # 基本的な照合結果
    best_match = result.get('best_match', {})
    print(f"[Best Match] -> {best_match.get('image_name', 'N/A')} (Score: {best_match.get('score', 0.0):.4f})")
    
    # 意図の語り
    print("\n--- Intent Narrative ---")
    print(result.get('intent_narrative', 'No intent narrative generated.'))
    
    # 成長の物語
    print("\n--- Growth Narrative ---")
    print(result.get('growth_narrative', 'No growth narrative generated.'))
    
    # 発見された時間的パターン
    patterns = result.get('discovered_temporal_patterns')
    if patterns:
        print("\n--- Discovered Temporal Patterns ---")
        for p in patterns:
            print(f"  - {p[0]} -> {p[1]}")

    # 倫理チェックの結果
    ethics_log = result.get('ethics_log')
    if ethics_log:
        print("\n--- Ethics Check (The Oath of the Eight) ---")
        for log_entry in ethics_log:
            print(f"  - {log_entry}")
            
    print(f"\n{'='*60}")

def main():
    parser = argparse.ArgumentParser(description="Run SigmaSense 16th Gen. Processing.")
    parser.add_argument(
        '--img_dir', 
        type=str, 
        default=os.path.join(project_root, "sigma_images"),
        help='Directory containing the input images.'
    )
    parser.add_argument(
        '--db_path', 
        type=str, 
        default=os.path.join(project_root, "config", "sigma_product_database_custom_ai_generated.json"),
        help='Path to the Sigma product database JSON file.'
    )
    args = parser.parse_args()

    print("--- Starting SigmaSense 16th Gen. Processing ---")
    
    # 意味データベースと次元定義の読み込み
    loader = DimensionLoader()
    database, ids, vectors = load_sigma_database(args.db_path)

    # SigmaSenseの初期化
    sigma = SigmaSense(
        database=database,
        ids=ids,
        vectors=vectors,
        generator=generator
    )

    # ロガーの初期化
    logger = ResponseLogger()

    # 対象画像群に対して思考サイクルを実行
    image_files = sorted([f for f in os.listdir(args.img_dir) if is_image_file(f)])
    if not image_files:
        print(f"No images found in '{args.img_dir}'. Halting.")
        return

    for fname in image_files:
        img_path = os.path.join(args.img_dir, fname)

        # 新しい思考サイクルを実行
        result = sigma.process_experience(img_path)

        # 結果をコンソールに表示
        display_unified_result(result)

        # 完全な結果をログに記録
        cleaned_result = convert_numpy_types(result)
        logger.log(cleaned_result)

    print(f"\n✅ All {len(image_files)} images processed.")
    print(f"Log saved to {logger.log_path}")
    print(f"Knowledge graph saved to {sigma.world_model.graph_path}")
    print(f"Memory log saved to {sigma.memory_graph.memory_path}")

if __name__ == "__main__":
    main()

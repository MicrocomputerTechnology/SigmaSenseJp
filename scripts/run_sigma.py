# === 第十六次実験 実行スクリプト ===

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigmasense.sigma_database_loader import load_sigma_database
from src.sigmasense.sigma_sense import SigmaSense
from src.selia.response_logger import ResponseLogger
from src.sigmasense.dimension_loader import DimensionLoader
import numpy as np
import argparse
import time

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
        default=os.path.join(project_root, "data", "world_model.sqlite"),
        help='Path to the Sigma product database JSON file.'
    )
    parser.add_argument(
        '--continuous', 
        action='store_true', 
        help='Run in continuous mode, monitoring img_dir for new images.'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=5, 
        help='Interval in seconds to check for new images in continuous mode.'
    )
    args = parser.parse_args()

    print("--- Starting SigmaSense 16th Gen. Processing ---")
    
    # 意味データベースと次元定義の読み込み
    loader = DimensionLoader()
    database, ids, vectors, layers = load_sigma_database(args.db_path)

    # SigmaSenseの初期化
    sigma = SigmaSense(
        database,
        ids,
        vectors,
        layers,
        dimension_loader=loader
    )

    # ロガーの初期化
    logger = ResponseLogger()

    processed_files = set() # 処理済みのファイルを追跡

    def process_images_in_directory():
        nonlocal processed_files
        current_image_files = sorted([f for f in os.listdir(args.img_dir) if is_image_file(f)])
        new_files_found = False

        for fname in current_image_files:
            if fname not in processed_files:
                img_path = os.path.join(args.img_dir, fname)
                print(f"\n--- Processing new image: {fname} ---")
                
                # 新しい思考サイクルを実行
                result = sigma.process_experience(img_path)

                if result:
                    # 結果をコンソールに表示
                    display_unified_result(result)

                    # 完全な結果をログに記録
                    cleaned_result = convert_numpy_types(result)
                    logger.log(cleaned_result)
                
                processed_files.add(fname)
                new_files_found = True
        return new_files_found

    # 初回実行
    print("--- Initial image processing ---")
    process_images_in_directory()
    print(f"✅ Initial processing complete. {len(processed_files)} images processed.")

    if args.continuous:
        print(f"--- Continuous mode enabled. Monitoring '{args.img_dir}' for new images every {args.interval} seconds ---")
        try:
            while True:
                time.sleep(args.interval)
                print(f"--- Checking for new images in '{args.img_dir}' ---")
                new_files_processed = process_images_in_directory()
                if not new_files_processed:
                    print("No new images found.")
        except KeyboardInterrupt:
            print("\n--- Continuous mode interrupted by user. Shutting down. ---")
    else:
        print("--- Batch processing complete. ---")

    print(f"\n✅ All processed images logged to {logger.log_path}")
    print(f"Knowledge graph saved to {sigma.world_model.store.db_path}")
    print(f"Memory log saved to {sigma.memory_graph.store.db_path}")

if __name__ == "__main__":
    main()

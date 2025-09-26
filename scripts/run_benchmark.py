import os
import sys
import numpy as np
from collections import Counter

# プロジェクトのルートをシステムパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_database_loader import load_sigma_database
from src.sigma_sense import SigmaSense
from src.dimension_loader import DimensionLoader

# プロジェクトのルートディレクトリ
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_expected_label(filename):
    """
    ファイル名から期待されるラベルを抽出する。
    例: 'circle_center_red.jpg' -> 'circle'
    """
    if not filename:
        return "unknown"
    # ファイル名の最初の部分をラベルとする
    return filename.split('_')[0]

def run_benchmark():
    """
    sigma_imagesデータセットに対して分類精度ベンチマークを実行する。
    """
    print("--- Running Benchmark for Geometric Shape Classification ---")

    # --- SigmaSenseの初期化 ---
    db_path = os.path.join(project_root, "config", "sigma_product_database_stabilized.json")
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        print("Please run 'python src/build_database.py' first.")
        return None, 0, 0

    loader = DimensionLoader()
    database, ids, vectors, layers = load_sigma_database(db_path)

    # DimensionGeneratorの初期化時にモデルパスを渡す必要があるか確認
    # run_sigma.pyでは引数なしで初期化しているため、それに倣う
    sigma = SigmaSense(
        database,
        ids,
        vectors,
        layers,
        dimension_loader=loader
    )

    # --- 評価データセットの準備 ---
    image_dir = os.path.join(project_root, "sigma_images")
    try:
        image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except FileNotFoundError:
        print(f"Error: Image directory not found at {image_dir}")
        return None, 0, 0
    
    # 'multi_object.jpg' と 'overlap_object.jpg' は単一の形状ではないため除外
    image_files = [f for f in image_files if 'multi' not in f and 'overlap' not in f]

    if not image_files:
        print(f"Warning: No suitable image files found in {image_dir}")
        return 0, 0, 0

    # --- ベンチマークの実行 ---
    correct_predictions = 0
    total_images = len(image_files)
    results = []

    print("\n--- Classification Details ---")
    for filename in image_files:
        image_path = os.path.join(image_dir, filename)
        expected_label = get_expected_label(filename)
        
        # SigmaSenseで分類を実行
        # process_experienceからの出力を受け取る
        result = sigma.process_experience(image_path)
        predicted_filename = result.get('best_match', {}).get('image_name', '')
        predicted_label = get_expected_label(predicted_filename)

        is_correct = (expected_label == predicted_label)
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        results.append({
            "file": filename,
            "expected": expected_label,
            "predicted": predicted_label,
            "status": status
        })
        print(f"  - Processing: {filename:<25} -> Expected: {expected_label:<10} | Predicted: {predicted_label:<10} | {status}")

    # --- 結果の集計と表示 ---
    accuracy = (correct_predictions / total_images) * 100 if total_images > 0 else 0

    print("\n--- Benchmark Results ---")
    print(f"Total Images Tested: {total_images}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy:            {accuracy:.2f}%")
    print("---------------------------\n")

    return accuracy, total_images, correct_predictions

if __name__ == "__main__":
    run_benchmark()

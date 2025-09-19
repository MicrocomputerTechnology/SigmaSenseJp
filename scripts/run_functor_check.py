
import os
import sys
import numpy as np

# 親ディレクトリ（プロジェクトルート）をパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.sigma_sense import SigmaSense
from src.sigma_database_loader import load_sigma_database
from src.sigma_functor import SigmaFunctor
from src.dimension_loader import dimension_loader
from src import image_transformer as it
from src import vector_transformer as vt

def print_header(title):
    bar = "="*70
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

def main():
    print_header("Functoriality Consistency Check")

    # --- 1. SigmaSenseの初期化 ---
    # 関手性チェックはデータベースとの比較を必要としないため、ダミーのDBで初期化
    try:
        database, ids, vectors = load_sigma_database("sigma_product_database_custom_ai_generated.json")
        sigma_instance = SigmaSense(database, ids, vectors)
        print("SigmaSense instance created successfully.")
    except Exception as e:
        print(f"Error initializing SigmaSense: {e}")
        return

    # --- 2. Functorの初期化 ---
    # FunctorはSigmaSenseのインスタンスを内部で利用する
    functor = SigmaFunctor(sigma_instance)
    print("SigmaFunctor instance created successfully.")

    # --- 3. テストケースの定義 ---
    # (画像ファイル, 画像変換, ベクトル変換, 変換名)
    test_cases = [
        ("circle_center.jpg", it.rotate_90, vt.transform_for_rotation, "90-degree Rotation"),
        ("pentagon_center.jpg", it.add_red_tint, vt.transform_for_red_tint, "Red Tint"),
        ("circle_center_red.jpg", it.convert_to_grayscale, vt.transform_for_grayscale, "Grayscale Conversion"),
        ("square_left.jpg", it.identity, vt.identity, "Identity (No-Op)"),
    ]
    image_dir = "sigma_images/"

    # --- 4. 検証の実行とレポート ---
    print_header("Running Consistency Checks")
    all_passed = True
    for image_file, image_transform, vector_transform, name in test_cases:
        print(f"\n--- Test Case: {name} on {image_file} ---")
        image_path = os.path.join(image_dir, image_file)
        if not os.path.exists(image_path):
            print(f"  -> ⚠️ SKIPPED: Image file not found at {image_path}")
            continue

        diff, is_consistent, actual_vector, expected_vector = functor.check_functoriality(image_path, image_transform, vector_transform)

        if diff is None:
            print(f"  -> ⚠️ SKIPPED: Vector generation failed for this test case.")
            continue

        if is_consistent:
            print(f"  -> ✅ PASSED: Functoriality holds. (Difference: {diff:.6f})")
        else:
            all_passed = False
            print(f"  -> ❌ FAILED: Functoriality broken. (Difference: {diff:.6f}) > 0.1")
            
            # --- 予期せず変化した次元の詳細レポート機能 ---
            vector_diff = np.abs(actual_vector - expected_vector)
            unexpected_change_indices = np.where(vector_diff > 0.01)[0]
            
            print("    Unexpected changes detected in the following dimensions:")
            for i in unexpected_change_indices:
                dim_id = dimension_loader.get_id(i) or f"Unknown Index {i}"
                print(f"      - {dim_id:<35} (Diff: {vector_diff[i]:.4f}, Actual: {actual_vector[i]:.4f}, Expected: {expected_vector[i]:.4f})")

    print_header("Final Report")
    if all_passed:
        print("🎉 Congratulations! All functoriality checks passed.")
    else:
        print("🔥 Some functoriality checks failed. Review the output above.")

if __name__ == "__main__":
    main()

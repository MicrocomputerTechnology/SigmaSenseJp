import sys
import os
import json
import numpy as np
import argparse

# 親ディレクトリをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root, 'src'))

from sigmasense.sigma_sense import SigmaSense
from sigmasense.dimension_loader import DimensionLoader

def test_single_image_vector(image_path):
    """単一の画像を指定して、その複合意味ベクトルを計算し、結果を詳細に表示する"""
    print(f"🧪 ベクトル生成テストを開始します...")
    print(f"   対象画像: {image_path}")
    print("-" * 70)

    if not os.path.exists(image_path):
        print(f"❗ エラー: 画像ファイルが見つかりません: {image_path}")
        return

    # --- SigmaSenseを初期化 ---
    config_dir = os.path.join(project_root, 'config')
    dim_paths = [
        os.path.join(config_dir, 'vector_dimensions_custom_ai.json'),
        os.path.join(config_dir, 'vector_dimensions_custom_ai_lyra.json')
    ]
    
    # DimensionLoaderを先にインスタンス化
    dim_loader = DimensionLoader(paths=dim_paths)
    all_dimensions = dim_loader.get_dimensions()
    vector_size = len(all_dimensions)
    dummy_vectors = np.empty((0, vector_size), dtype=np.float32)

    # Loaderを注入してSigmaSenseをインスタンス化
    sigma = SigmaSense([], [], dummy_vectors, [], dimension_loader=dim_loader)

    # --- ベクトルを計算 ---
    # 再構成は詳細な値を見る上でノイズになるため無効化
    result = sigma.process_experience(image_path)
    vector = result.get('vector')

    if not vector:
        print("❗ ベクトルの生成に失敗しました。")
        return

    # --- 結果とマッピングして表示 ---
    if len(vector) != len(all_dimensions):
        print(f"❗ 警告: ベクトルの次元数({len(vector)})と定義の次元数({len(all_dimensions)})が一致しません。")

    print("📊 計算結果:")
    # TODO: The distinction between Selia and Lyra dimensions is no longer easily accessible
    # after the DimensionLoader refactoring. This report now shows all dimensions together.
    print("\n--- All Dimensions ---")
    for i, dim in enumerate(all_dimensions):
        val = vector[i]
        # 値が0.1より大きい場合にハイライト
        highlight = "🔥" if val > 0.1 else "  "
        layer = dim.get('layer', 'unknown')
        print(f"  {highlight} [{layer.upper()}] {dim['id']:<30} | 値: {val:.4f} | {dim['name_ja']}")

    print("\n" + "-" * 70)
    print("✅ テスト完了。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='単一画像のベクトル生成をテストするスクリプト',
        epilog="実行例: python tools/run_vector_generation_test.py --image_path sigma_images/circle_center.jpg",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--image_path', type=str, default='sigma_images/circle_center.jpg', help='テスト対象の画像ファイルへのパス')

    args = parser.parse_args()
    test_single_image_vector(args.image_path)

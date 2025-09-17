import sys
import os
import json
import numpy as np
import argparse

# 親ディレクトリをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sigma_sense import SigmaSense
from dimension_loader import DimensionLoader

def test_single_image_vector(image_path):
    """単一の画像を指定して、その複合意味ベクトルを計算し、結果を詳細に表示する"""
    print(f"🧪 ベクトル生成テストを開始します...")
    print(f"   対象画像: {image_path}")
    print("-" * 70)

    if not os.path.exists(image_path):
        print(f"❗ エラー: 画像ファイルが見つかりません: {image_path}")
        return

    # --- SigmaSenseを初期化 ---
    selia_dim_path = os.path.join(project_root, 'vector_dimensions_custom_ai.json')
    lyra_dim_path = os.path.join(project_root, 'vector_dimensions_custom_ai_lyra.json')
    
    # DimensionLoaderを先にインスタンス化
    dim_loader = DimensionLoader(selia_path=selia_dim_path, lyra_path=lyra_dim_path)
    all_dimensions = dim_loader.get_dimensions()
    vector_size = len(all_dimensions)
    dummy_vectors = np.empty((0, vector_size), dtype=np.float32)

    # Loaderを注入してSigmaSenseをインスタンス化
    sigma = SigmaSense([], [], dummy_vectors, dimension_loader=dim_loader)

    # --- ベクトルを計算 ---
    # 再構成は詳細な値を見る上でノイズになるため無効化
    result = sigma.match(image_path, reconstruct=False)
    vector = result.get('vector')

    if not vector:
        print("❗ ベクトルの生成に失敗しました。")
        return

    # --- 結果とマッピングして表示 ---
    if len(vector) != len(all_dimensions):
        print(f"❗ 警告: ベクトルの次元数({len(vector)})と定義の次元数({len(all_dimensions)})が一致しません。")

    print("📊 計算結果:")
    # Selia次元の結果を表示
    print("\n--- Selia（構造）次元 ---")
    selia_len = len(dim_loader._selia_dims)

    for i in range(selia_len):
        dim = all_dimensions[i]
        val = vector[i]
        # 値が0.1より大きい場合にハイライト
        highlight = "🔥" if val > 0.1 else "  "
        print(f"  {highlight} {dim['id']:<35} | 値: {val:.4f} | {dim['name_ja']}")

    # Lyra次元の結果を表示
    print("\n--- Lyra（感性）次元 ---")
    for i in range(selia_len, len(all_dimensions)):
        dim = all_dimensions[i]
        val = vector[i]
        highlight = "🔥" if val > 0.1 else "  "
        print(f"  {highlight} {dim['id']:<35} | 値: {val:.4f} | {dim['name_ja']}")

    print("\n" + "-" * 70)
    print("✅ テスト完了。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='単一画像のベクトル生成をテストするスクリプト')
    parser.add_argument('image_path', type=str, help='テスト対象の画像ファイルへのパス')
    args = parser.parse_args()

    test_single_image_vector(args.image_path)

import os
import sys

# 親ディレクトリをパスに追加して、sigma_senseなどのモジュールをインポート可能にする
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import yaml
import numpy as np
from PIL import Image
import tempfile
import shutil
import json

# SigmaSenseのコア機能と、新しく定義した変換器をインポート
from src.sigma_sense import SigmaSense
from src.sigma_database_loader import load_sigma_database
from src.dimension_loader import DimensionLoader
from src.sigma_functor import SigmaFunctor  # <-- SigmaFunctorをインポート
from src import image_transformer as it
# from src import vector_transformer as vt # 現状未使用なのでコメントアウト

# ----------------------------------------------------------------------------
# 設定ファイルの読み込み
# ----------------------------------------------------------------------------

def load_octasense_config(config_path=None):
    """OctaSenseの設定ファイルを読み込む"""
    if config_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, 'config')
        config_path = os.path.join(config_dir, 'octasense_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# ----------------------------------------------------------------------------
# ベクトル変換関数の定義
# ----------------------------------------------------------------------------

def identity_vector_transform(vector):
    """ベクトルを何も変更しない恒等変換"""
    return vector

def add_red_tint_on_vector(vector, dimension_loader):
    """ベクトルの色彩次元（赤）を増加させる変換"""
    new_vector = vector.copy()
    # 'red_component'次元のインデックスを取得して値を増やす
    try:
        red_index = dimension_loader.get_index('red_component')
        if red_index is not None:
            new_vector[red_index] = min(1.0, new_vector[red_index] + 0.2)
    except (KeyError, ValueError):
        # 次元が存在しない場合は何もしない
        pass
    return new_vector

def rotate_90_then_add_red_tint(image):
    """画像を90度回転させてから赤色を付与する複合変換"""
    rotated_image = it.rotate_90(image)
    return it.add_red_tint(rotated_image)

def identity_then_add_red_tint_on_vector(vector, dimension_loader):
    """ベクトルを恒等変換してから色彩次元（赤）を増加させる複合変換"""
    identity_vector = identity_vector_transform(vector)
    return add_red_tint_on_vector(identity_vector, dimension_loader)

# ----------------------------------------------------------------------------
# 関手性検証の実行
# ----------------------------------------------------------------------------

def run_functoriality_check(functor, image_path, transform_f, transform_g, vector_transform_Ff, vector_transform_Fg, description):
    """
    指定された変換について関手性の検証を実行し、結果を表示する。
    """
    print(f"--- 関手性検証: {os.path.basename(image_path)} | 変換: {description} ---")
    
    result = functor.check_functoriality(
        original_image=image_path,
        transform_f=transform_f,
        transform_g=transform_g,
        vector_transform_Ff=vector_transform_Ff,
        vector_transform_Fg=vector_transform_Fg
    )

    if result is None:
        print("  🟡 結果: 検証不可 (画像のベクトル生成に失敗)")
        return False

    is_consistent = result["is_consistent"]
    diff_norm = result["difference"]

    if is_consistent:
        print(f"  ✅ 結果: 一貫性あり (差分ノルム: {diff_norm:.4f})")
    else:
        print(f"  ❗ 結果: 不一致 (差分ノルム: {diff_norm:.4f})")
        # ここで失敗ログを記録することも可能
    
    print("-" * 70)
    return is_consistent

def main():
    """メインの検証処理"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    
    octasense_config = load_octasense_config(os.path.join(config_dir, 'octasense_config.yaml'))
    print("OctaSense設定ファイルを正常に読み込みました。")
    print(f"詩名: {octasense_config['OctaSense']['poetic_name']}")

    db_path = os.path.join(config_dir, "sigma_product_database_custom_ai_generated.json")
    database, ids, vectors = load_sigma_database(db_path)
    
    dim_loader = DimensionLoader()
    sigma = SigmaSense(database, ids, vectors, dimension_loader=dim_loader)
    
    # SigmaFunctorをインスタンス化
    functor = SigmaFunctor(sigma)
    
    # --- テストケースの定義 ---
    # (画像ファイル名, 最初の画像変換関数 f, 次の画像変換関数 g,
    #  fに対応するベクトル変換 F(f), gに対応するベクトル変換 F(g), 説明)
    test_cases = [
        (
            "circle_center.jpg",
            it.rotate_90,
            it.add_red_tint,
            identity_vector_transform,
            lambda v: add_red_tint_on_vector(v, dim_loader),
            "回転後に赤色化 (形状不変性と色彩変化の検証)"
        ),
        (
            "pentagon_center.jpg",
            it.convert_to_grayscale,
            it.rotate_90, # Grayscale then rotate
            identity_vector_transform, # Grayscale might not have a direct vector transform if color dimensions are removed
            identity_vector_transform, # Rotation invariance
            "グレースケール後に回転 (色彩情報損失と形状不変性の検証)"
        ),
        # Add more test cases as needed
    ]

    image_dir = os.path.join(project_root, "sigma_images")
    results = []

    for base_image, transform_f, transform_g, vector_transform_Ff, vector_transform_Fg, description in test_cases:
        image_path = os.path.join(image_dir, base_image)
        if not os.path.exists(image_path):
            print(f"テスト画像が見つかりません: {image_path}")
            continue
        
        is_consistent = run_functoriality_check(functor, image_path, transform_f, transform_g, vector_transform_Ff, vector_transform_Fg, description)
        results.append(is_consistent)

    # --- サマリーレポート ---
    total = len(results)
    passed = sum(1 for r in results if r)
    print("\n" + "="*70)
    print("📊 関手性 検証サマリー")
    print("="*70)
    print(f"実行テスト数: {total}")
    print(f"パスしたテスト数: {passed}")
    if total > 0:
        print(f"成功率: {passed/total:.2%}")
    
    if passed < total:
        print("\n❌ 一貫性が確認できなかったテストがありました。")


if __name__ == "__main__":
    main()

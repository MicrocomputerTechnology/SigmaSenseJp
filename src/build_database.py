import os
import json
import sys
from tqdm import tqdm
import numpy as np
import argparse

# Add the src directory to the Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from dimension_generator_local import DimensionGenerator
from dimension_loader import DimensionLoader
from stabilize_database import stabilize_database
from correction_applicator import CorrectionApplicator

# --- NumPyデータ型をJSONに変換するためのカスタムエンコーダ ---
class NumpyEncoder(json.JSONEncoder):
    """ NumPyのデータ型をJSONシリアライズ可能にするためのカスタムエンコーダ """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# 定数
config_dir = os.path.join(project_root, "config")
SELIA_DIMS_PATH = os.path.join(config_dir, "vector_dimensions_custom_ai.json")
LYRA_DIMS_PATH = os.path.join(config_dir, "vector_dimensions_custom_ai_lyra.json")

def is_image_file(fname):
    """画像ファイルかどうかを判定する"""
    return fname.lower().endswith((".png", ".jpg", ".jpeg"))

def build_vector_from_facts(facts, dimension_loader):
    """
    次元定義に従って、特徴量の辞書から順序付けられたベクトルを構築する。
    """
    dimensions = dimension_loader.get_dimensions()
    vector = [0.0] * len(dimensions)
    for i, dim in enumerate(dimensions):
        dim_id = dim['id']
        value = facts.get(dim_id, 0.0)
        # 念のため、値がNoneでないことを確認
        if value is None:
            value = 0.0
        # numpyのbool型などが紛れ込むことがあるため、floatにキャスト
        try:
            vector[i] = float(value)
        except (ValueError, TypeError):
            vector[i] = 0.0 # 変換できない場合は0.0とする
    return vector

def _get_dominant_layer(vector, dimension_loader):
    """
    ベクトルの中で最も値が大きい次元のレイヤーを特定する。
    """
    dimensions = dimension_loader.get_dimensions()
    if not vector or len(vector) != len(dimensions):
        return "unknown"

    max_val_index = np.argmax(vector)
    if max_val_index < len(dimensions):
        return dimensions[max_val_index].get("layer", "unknown")
    return "unknown"

def build_database(img_dir, db_path, dimension_config_path):
    print("DEBUG: build_database called")
    """sigma_imagesディレクトリ内の画像から最新のアーキテクチャに基づいた意味データベースを構築する"""
    print(f"🚀 最新アーキテクチャでの意味データベース構築を開始します...")
    print(f"   画像ディレクトリ: {img_dir}")
    print(f"   出力先: {db_path}")

    # 最新の次元生成器と次元定義ローダーを初期化
    dim_generator = DimensionGenerator()
    
    # dimension_config_path を使ってDimensionLoaderを初期化
    if dimension_config_path:
        print(f"   指定された次元ファイルを使用: {dimension_config_path}")
        dim_loader = DimensionLoader(paths=[dimension_config_path])
    else:
        print("   デフォルトの全次元ファイルを使用します。")
        dim_loader = DimensionLoader() # 指定がない場合はデフォルト

    database = []
    if not os.path.isdir(img_dir):
        print(f"❗ エラー: 画像ディレクトリが見つかりません: {img_dir}")
        return

    image_files = [f for f in sorted(os.listdir(img_dir)) if is_image_file(f)]

    if not image_files:
        print("❗ 警告: 対象となる画像ファイルが見つかりません。")
        return

    # tqdmを使ってプログレスバーを表示
    for fname in tqdm(image_files, desc="ベクトル生成中"):
        img_path = os.path.join(img_dir, fname)
        item_id = os.path.splitext(fname)[0]
        
        # 1. 特徴量を網羅的に抽出
        generation_result = dim_generator.generate_dimensions(img_path)
        facts = generation_result.get("features", {})

        if not facts:
            print(f"⚠️ 警告: {fname} の特徴量抽出に失敗したため、データベースから除外します。")
            continue

        # 2. 次元定義に従ってベクトルを構築
        vector = build_vector_from_facts(facts, dim_loader)
        
        # 3. ベクトルの主要レイヤーを判定
        layer = _get_dominant_layer(vector, dim_loader)

        database.append({
            "id": item_id,
            "meaning_vector": vector,
            "layer": layer
        })

    # --- データベース全体に一貫性補正を適用 ---
    corrector = CorrectionApplicator()
    stabilized_database = corrector.apply_to_database(database)

    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(stabilized_database, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print(f"\n✅ データベースの構築と安定化が完了しました。{len(stabilized_database)}件のデータが {db_path} に保存されました。")
    except IOError as e:
        print(f"\n❗ エラー: データベースファイルの書き込みに失敗しました: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build the SigmaSense product database from a directory of images.",
        epilog="Example: python src/build_database.py --img_dir sigma_images",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--img_dir', type=str, default='sigma_images', help='Directory containing the images.')
    parser.add_argument("--db_path", type=str, default="config/sigma_product_database_stabilized.json",
                        help="Path to the output SigmaSense product database JSON file.")
    parser.add_argument("--dimension_config", type=str, default=None,
                        help="Path to a specific dimension configuration file (YAML or JSON). \nIf not provided, all default dimension files will be used.")
    
    # 引数が渡されなかった場合に、エラーメッセージとヘルプを表示
    if len(sys.argv) == 1:
        print("エラー: 画像ディレクトリが指定されていません。--img_dir 引数を使用してください。\n")
        parser.print_help()
        sys.exit(1)

    try:
        args = parser.parse_args()
        build_database(args.img_dir, args.db_path, args.dimension_config)
    except SystemExit as e:
        # argparseが引数エラーで終了しようとした場合、ここでキャッチして追加情報を提供
        # (このロジックは、引数が一部不足している場合などに役立つ)
        if e.code != 0:
            print("\n引数の指定に誤りがあるようです。使い方を確認してください。")
        # parser.print_help() # 必要に応じてヘルプを再表示
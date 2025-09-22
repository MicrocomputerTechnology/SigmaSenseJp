import os
import json
import sys
from tqdm import tqdm
import numpy as np

# プロジェクトルートを定義
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from .dimension_generator_local import DimensionGenerator
from .dimension_loader import DimensionLoader
from .correction_applicator import CorrectionApplicator

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
IMG_DIR = os.path.join(project_root, "sigma_images")
DB_PATH = os.path.join(config_dir, "sigma_product_database_custom_ai_generated.json")
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

def build_database(img_dir=IMG_DIR, db_path=DB_PATH):
    print("DEBUG: build_database called")
    """sigma_imagesディレクトリ内の画像から最新のアーキテクチャに基づいた意味データベースを構築する"""
    print(f"🚀 最新アーキテクチャでの意味データベース構築を開始します...")
    print(f"   画像ディレクトリ: {img_dir}")
    print(f"   出力先: {db_path}")

    # 最新の次元生成器と次元定義ローダーを初期化
    dim_generator = DimensionGenerator()
    dim_loader = DimensionLoader() # 引数なしで初期化し、デフォルトの全次元ファイルを読み込む

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

        database.append({
            "id": item_id,
            "meaning_vector": vector
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
    build_database()
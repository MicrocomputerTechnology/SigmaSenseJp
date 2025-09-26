import os
import sys
import pytest

# プロジェクトのルートをシステムパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_database_loader import load_sigma_database
from src.sigma_sense import SigmaSense
from src.dimension_loader import DimensionLoader

# プロジェクトのルートディレクトリ
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="module")
def sigma_instance():
    """
    テスト用のSigmaSenseインスタンスを生成するフィクスチャ
    """
    db_path = os.path.join(project_root, "config", "sigma_product_database_stabilized.json")
    if not os.path.exists(db_path):
        pytest.fail(f"Database file not found at {db_path}. Run 'python src/build_database.py --img_dir sigma_images' first.")

    loader = DimensionLoader()
    database, ids, vectors, layers = load_sigma_database(db_path)

    sigma = SigmaSense(
        database,
        ids,
        vectors,
        layers,
        dimension_loader=loader
    )
    return sigma

def get_expected_label(filename):
    if not filename:
        return "unknown"
    return filename.split('_')[0]

# テストケースを動的に生成するためのデータ
# 正解が期待されるものと、既知の失敗ケースを含む
test_data = [
    ("circle_center.jpg", "circle"),
    ("square_left.jpg", "square"),
    ("triangle_top.jpg", "triangle"),
    ("line_diagonal.jpg", "line"),
    # 現在の実装では誤分類されることがわかっているケース
    pytest.param("hexagon_center.jpg", "hexagon", marks=pytest.mark.xfail(reason="Known issue: hexagon is misclassified as overlap")),
    pytest.param("pentagon_center.jpg", "pentagon", marks=pytest.mark.xfail(reason="Known issue: pentagon is misclassified as overlap")),
    pytest.param("pentagon_center_blue.jpg", "pentagon", marks=pytest.mark.xfail(reason="Known issue: layer detection fails for colored pentagon")),
]

@pytest.mark.parametrize("image_file, expected_shape", test_data)
def test_shape_classification(sigma_instance, image_file, expected_shape):
    """
    個別の画像が期待通りに分類されるか（または既知の不具合としてxfailするか）をテストする。
    """
    image_path = os.path.join(project_root, "sigma_images", image_file)
    
    result = sigma_instance.process_experience(image_path)
    predicted_filename = result.get('best_match', {}).get('image_name', '')
    predicted_label = get_expected_label(predicted_filename)
    
    assert predicted_label == expected_shape

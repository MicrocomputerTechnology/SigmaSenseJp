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
from src import image_transformer as it
from src import vector_transformer as vt

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
# 関手性検証フレームワーク
# ----------------------------------------------------------------------------

class FunctorValidator:
    """
    SigmaSenseが関手(Functor)の法則を満たすか、またOctaSenseの軸に沿った一貫性を持つかを検証する。
    """
    def __init__(self, sigma_instance, failure_log_path=None):
        if failure_log_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            log_dir = os.path.join(project_root, 'sigma_logs')
            self.failure_log_path = os.path.join(log_dir, "functor_consistency_failures.jsonl")
        else:
            self.failure_log_path = failure_log_path

        self.sigma = sigma_instance
        self.dimension_loader = sigma_instance.dimension_loader  # Get loader from SigmaSense
        self.results = []
        # ログファイルを初期化
        with open(self.failure_log_path, 'w') as f:
            pass # ファイルを空にする

    def _get_vector(self, image_path_or_pil):
        """画像パスまたはPIL.Imageから意味ベクトルを生成する"""
        if isinstance(image_path_or_pil, str):
            if not os.path.exists(image_path_or_pil):
                print(f"  ❗エラー: 画像ファイルが見つかりません: {image_path_or_pil}")
                return None
            return self.sigma.process_experience(image_path_or_pil)['vector']
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image_path_or_pil.save(tmp.name, "PNG")
            vec = self.sigma.process_experience(tmp.name)['vector']
        os.remove(tmp.name)
        return np.array(vec)

    def check_axis_consistency(self, base_image_path, transform, expected_axis, description):
        """
        画像変換が、意図した意味軸の次元にのみ影響を与えるかを検証する。
        """
        print(f"--- 軸一貫性検証: {os.path.basename(base_image_path)} | 変換: {description} | 期待軸: {expected_axis} ---")

        vec_before = self._get_vector(base_image_path)
        if vec_before is None: return

        transformed_image = transform(Image.open(base_image_path).convert('RGB'))
        vec_after = self._get_vector(transformed_image)
        if vec_after is None: return

        vector_diff = np.abs(vec_after - vec_before)
        changed_indices = np.where(vector_diff > 0.01)[0]
        expected_indices = self.dimension_loader.get_indices_for_axis(expected_axis)
        is_consistent = all(idx in expected_indices for idx in changed_indices)
        
        result = {
            "image": os.path.basename(base_image_path),
            "transform": description,
            "transform_func": transform.__name__,
            "expected_axis": expected_axis,
            "consistent": is_consistent,
            "changed_indices": changed_indices.tolist(),
            "expected_indices": expected_indices,
            "vector_diff": vector_diff.tolist(),
            "norm_diff": np.linalg.norm(vec_after - vec_before)
        }
        self.results.append(result)

        if is_consistent:
            print(f"  ✅ 結果: 一貫性あり (差分: {result['norm_diff']:.4f})")
        else:
            unexpected_indices = [idx for idx in changed_indices if idx not in expected_indices]
            print(f"  ❗ 結果: 不一致 (差分: {result['norm_diff']:.4f})")
            print("    予期せず変化した次元:")
            for i in unexpected_indices:
                dim_id = self.dimension_loader.get_id(i)
                print(f"      - {dim_id:<22} (Index: {i}, Diff: {vector_diff[i]:.4f})")
            # 失敗ログを記録
            self._log_failure(result)
        print("-" * 70)

    def _log_failure(self, failure_data):
        """一貫性チェックの失敗をJSONL形式で記録する"""
        with open(self.failure_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(failure_data) + '\n')

    def report(self):
        """検証結果のサマリーを報告"""
        total = len(self.results)
        if total == 0:
            print("テストは実行されませんでした。")
            return
            
        passed = sum(1 for r in self.results if r['consistent'])
        print("\n" + "="*70)
        print("📊 軸一貫性 検証サマリー")
        print("="*70)
        print(f"実行テスト数: {total}")
        print(f"パスしたテスト数: {passed}")
        print(f"成功率: {passed/total:.2%}")
        if passed < total:
            print("\n❌ 不一致だったテスト:")
            for r in self.results:
                if not r['consistent']:
                    print(f"  - 画像: {r['image']}, 変換: {r['transform']}, 期待軸: {r['expected_axis']}")
            print(f"\n📝 詳細な失敗ログは {self.failure_log_path} を確認してください。")

def main():
    """メインの検証処理"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    log_dir = os.path.join(project_root, 'sigma_logs')
    
    octasense_config = load_octasense_config(os.path.join(config_dir, 'octasense_config.yaml'))
    print("OctaSense設定ファイルを正常に読み込みました。")
    print(f"詩名: {octasense_config['OctaSense']['poetic_name']}")

    db_path = os.path.join(config_dir, "sigma_product_database_custom_ai_generated.json")
    database, ids, vectors = load_sigma_database(db_path)
    
    # 最新の方法でSigmaSenseをインスタンス化
    dim_loader = DimensionLoader()
    sigma = SigmaSense(database, ids, vectors, dimension_loader=dim_loader)
    
    # ログファイル名を指定してValidatorを初期化
    log_path = os.path.join(log_dir, "functor_consistency_failures.jsonl")
    validator = FunctorValidator(sigma, failure_log_path=log_path)
    
    test_cases = [
        ("circle_center.jpg", it.add_red_tint, "彩", "赤色化"),
        ("pentagon_center.jpg", it.convert_to_grayscale, "彩", "グレースケール化"),
        ("circle_center.jpg", it.shift_left, "座", "左へシフト"),
    ]

    image_dir = os.path.join(project_root, "sigma_images")

    for base_image, transform, axis, description in test_cases:
        image_path = os.path.join(image_dir, base_image)
        validator.check_axis_consistency(image_path, transform, axis, description)

    validator.report()

if __name__ == "__main__":
    main()

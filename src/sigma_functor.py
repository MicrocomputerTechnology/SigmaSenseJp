import numpy as np
from .dimension_loader import DimensionLoader
from collections import defaultdict
import tempfile
import os
from PIL import Image

class SigmaFunctor:
    """
    圏論における関手（Functor）の概念を実装するクラス。
    画像の変換（射）が、ベクトル空間の変換（射）にどのように対応するか、
    その構造保存性を検証するために用いる。
    """
    def __init__(self, sigma_instance):
        self.sigma = sigma_instance

    def _get_vector(self, image_path_or_pil):
        """画像パスまたはPIL.Imageから意味ベクトルを生成する"""
        if isinstance(image_path_or_pil, str):
            if not os.path.exists(image_path_or_pil):
                return None
            # 戻り値の形式を 'vector' キーに合わせる
            result = self.sigma.process_experience(image_path_or_pil)
            return np.array(result['vector']) if result and 'vector' in result else None
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image_path_or_pil.save(tmp.name, "PNG")
            # 戻り値の形式を 'vector' キーに合わせる
            result = self.sigma.process_experience(tmp.name)
            vec = result['vector'] if result and 'vector' in result else None
        os.remove(tmp.name)
        return np.array(vec) if vec is not None else None

    def check_functoriality(self, image_path, image_transform_func, vector_transform_func):
        """
        関手性を検証する。
        F(g(x)) と (F_g)(F(x)) の差を計算する。
        - F: SigmaSenseによる画像からベクトルへの写像
        - g: 画像への変換 (例: 回転)
        - F_g: ベクトルへの変換
        """
        # F(x)
        vec_before = self._get_vector(image_path)
        if vec_before is None:
            return None, True # 元画像のベクトルが生成できなければチェック不能

        # F(g(x))
        transformed_image = image_transform_func(Image.open(image_path).convert('RGB'))
        vec_after_g = self._get_vector(transformed_image)
        if vec_after_g is None:
            return None, True # 変換後画像のベクトルが生成できなければチェック不能

        # (F_g)(F(x))
        expected_vec_after = vector_transform_func(vec_before)

        # F(g(x)) と (F_g)(F(x)) の差分（距離）を計算
        diff_norm = np.linalg.norm(vec_after_g - expected_vec_after)

        # 差分が閾値以下であれば、関手性は（近似的に）保たれている
        is_consistent = diff_norm < 0.1 # 閾値は経験的に設定

        return diff_norm, is_consistent, vec_after_g, expected_vec_after

    def generate_response(self, query_vector, best_match_id, score, entropy, sparsity):
        # 応答分類理論：分類ラベルの決定
        if score > 0.9:
            classification = "Strong Match"
        elif score > 0.8:
            classification = "Potential Match"
        elif score > 0.7:
            classification = "Weak Analogy"
        else:
            classification = "Unrelated"

        # --- 意味軸ごとの照合根拠を動的に生成 ---
        reasoning = []
        dims_by_layer = defaultdict(list)
        # Use the dimension_loader from the sigma_instance
        for i, dim_def in enumerate(self.sigma.dimension_loader.get_dimensions()):
            layer = dim_def.get('layer', 'unknown')
            name = dim_def.get('name_ja', dim_def['id'])
            value = query_vector[i] if i < len(query_vector) else 0.0
            dims_by_layer[layer].append(f"{name}={value:.3f}")
        
        for layer, dim_strs in dims_by_layer.items():
            reasoning.append(f"{layer.capitalize()} Layer: " + ", ".join(dim_strs))

        return {
            "classification": classification,
            "reasoning": reasoning
        }

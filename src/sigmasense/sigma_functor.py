import numpy as np
import os
import tempfile
from PIL import Image
from collections import defaultdict
import inspect

from sigma_image_engines.engine_opencv import OpenCVEngine

class SigmaFunctor:
    def __init__(self, vector_transforms, sigma_instance=None):
        self.vector_transforms = vector_transforms
        self.sigma = sigma_instance # SigmaSense instance for dimension_loader

    def _get_features(self, image_path_or_pil):
        """画像パスまたはPIL.Imageから生の特徴量辞書を生成する"""
        # OpenCVEngineを直接使用して特徴量を抽出
        engine = OpenCVEngine()
        if isinstance(image_path_or_pil, str):
            if not os.path.exists(image_path_or_pil):
                return None
            features = engine.extract_features(image_path_or_pil)
        else:
            # PIL Imageを一時ファイルに保存してパスを渡す
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                image_path_or_pil.save(tmp.name, "PNG")
                features = engine.extract_features(tmp.name)
            os.remove(tmp.name)
        return features

    def check_functoriality(self, image_path, image_transform_func, vector_transform_func_name, *args, **kwargs):
        """
        関手性を検証する。
        F(g(x)) と (F_g)(F(x)) の差を計算する。
        - F: OpenCVEngineによる画像から生の特徴量辞書への写像
        - g: 画像への変換 (例: 回転)
        - F_g: 特徴量辞書への変換 (vector_transform_func_nameで指定されたVectorTransformsのメソッド)
        """
        # F(x)
        features_before = self._get_features(image_path)
        if features_before is None:
            return None, True # 元画像のベクトルが生成できなければチェック不能

        # F(g(x))
        transformed_image = image_transform_func(Image.open(image_path).convert('RGB'))
        features_after_g = self._get_features(transformed_image)
        if features_after_g is None:
            return None, True # 変換後画像のベクトルが生成できなければチェック不能

        # (F_g)(F(x))
        # vector_transform_func_nameからVectorTransformsのメソッドを取得
        if not hasattr(self.vector_transforms, vector_transform_func_name):
            raise AttributeError(f"VectorTransforms does not have method: {vector_transform_func_name}")
        
        vector_transform_method = getattr(self.vector_transforms, vector_transform_func_name)
        vector_transform_method = getattr(self.vector_transforms, vector_transform_func_name)
        sig = inspect.signature(vector_transform_method)
        if 'dimension_loader' in sig.parameters:
            expected_features_after = vector_transform_method(features_before, self.sigma.dimension_loader, *args, **kwargs)
        else:
            expected_features_after = vector_transform_method(features_before, *args, **kwargs)

        # F(g(x)) と (F_g)(F(x)) の差分（距離）を計算
        # 特徴量辞書内の関連する数値特徴量のみを比較
        diff_sum = 0.0
        num_compared_features = 0

        # 比較する特徴量のIDを明示的に指定
        # Hu Moments (2), Fourier Descriptors (5), Dominant Hue (1), Avg Saturation (1), Edge Density (1)
        # Total 10 features
        feature_ids_to_compare = [
            "opencv_hu_moment_1", "opencv_hu_moment_2",
            "opencv_fourier_descriptor_1", "opencv_fourier_descriptor_2",
            "opencv_fourier_descriptor_3", "opencv_fourier_descriptor_4",
            "opencv_fourier_descriptor_5",
            "opencv_dominant_hue", "opencv_avg_saturation", "opencv_edge_density"
        ]

        for fid in feature_ids_to_compare:
            val_g = features_after_g.get(fid)
            val_expected = expected_features_after.get(fid)

            if isinstance(val_g, (float, int)) and isinstance(val_expected, (float, int)):
                diff_sum += abs(val_g - val_expected)
                num_compared_features += 1
            elif isinstance(val_g, np.ndarray) and isinstance(val_expected, np.ndarray):
                if val_g.shape == val_expected.shape:
                    diff_sum += np.linalg.norm(val_g - val_expected)
                    num_compared_features += 1

        diff_norm = diff_sum / num_compared_features if num_compared_features > 0 else 0.0

        # 差分が閾値以下であれば、関手性は（近似的に）保たれている
        is_consistent = diff_norm < 0.1 # 閾値は経験的に設定

        return diff_norm, is_consistent, features_after_g, expected_features_after

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
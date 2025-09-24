
import numpy as np
from PIL import Image
import os
import tensorflow as tf

class MobileViTEngine:
    """
    An engine that uses a real MobileViT TensorFlow SavedModel to extract features.
    """
    def __init__(self, model_path="models/mobilevit-tensorflow2-xxs-1k-256-v1", config=None):
        print("Initializing REAL MobileViT (TensorFlow SavedModel) Engine...")
        self.model_path = model_path
        self.model = None
        if not os.path.isdir(self.model_path):
            print(f"!!! ERROR: SavedModel directory not found at {self.model_path} !!!")
            return
        try:
            self.model = tf.saved_model.load(self.model_path)
            self.infer = self.model.signatures["serving_default"]
            # 動的な入力サイズ取得が失敗したため、モデル名からサイズを256x256と仮定します
            self.input_height = 256
            self.input_width = 256
            print(f"TensorFlow SavedModel loaded successfully from {model_path}.")
            print(f"Using assumed input shape: ({self.input_height}, {self.input_width})")
        except Exception as e:
            print(f"!!! ERROR: Failed to load SavedModel from {self.model_path} !!!")
            print(f"Error: {e}")
            self.model = None

    def _preprocess_image(self, image_path_or_obj):
        if isinstance(image_path_or_obj, str):
            img = Image.open(image_path_or_obj).convert('RGB')
        else:
            img = image_path_or_obj.convert('RGB')

        img = img.resize((self.input_width, self.input_height))
        input_data = np.array(img, dtype=np.float32) / 255.0
        input_data = np.expand_dims(input_data, axis=0)
        return tf.constant(input_data)

    def extract_features(self, image_path_or_obj):
        if not self.model:
            print(f"MobileViT: Model not loaded. Skipping feature extraction.")
            return {}

        try:
            input_tensor = self._preprocess_image(image_path_or_obj)
            
            # 推論関数を直接呼び出します
            output_dict = self.infer(input_tensor)
            
            # 出力辞書から最初のエントリを特徴ベクトルとして取得します
            output_key = list(output_dict.keys())[0]
            feature_vector = output_dict[output_key].numpy()[0]
            
            return {
                "mobilevit_feature_mean": float(np.mean(feature_vector)),
                "mobilevit_feature_std": float(np.std(feature_vector)),
                "mobilevit_feature_max": float(np.max(feature_vector)),
            }
        except Exception as e:
            print(f"Error during MobileViT (SavedModel) inference: {e}")
            return {}

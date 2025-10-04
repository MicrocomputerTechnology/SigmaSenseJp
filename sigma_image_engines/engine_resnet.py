
import numpy as np
from PIL import Image
import os
import tensorflow as tf
import tensorflow_hub as hub

class ResNetEngine:
    """
    An engine that uses a real ResNet V2 50 TensorFlow SavedModel to extract features.
    """
    def __init__(self, model_path="models/resnet_v2_50_saved_model", config=None):
        print("Initializing REAL ResNet V2 50 (TensorFlow Hub) Engine...")
        self.model_path = model_path
        self.model = None
        if not os.path.isdir(self.model_path):
            print(f"!!! ERROR: SavedModel directory not found at {self.model_path} !!!")
            return
        try:
            # Load the model as a KerasLayer
            self.model = hub.KerasLayer(self.model_path)
            # Input size for ResNet V2 50 is 224x224
            self.input_height = 224
            self.input_width = 224
            print(f"TensorFlow Hub Layer loaded successfully from {model_path}.")
            print(f"Using input shape: ({self.input_height}, {self.input_width})")
        except Exception as e:
            print(f"!!! ERROR: Failed to load model from {self.model_path} !!!")
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
            print("ResNet: Model not loaded. Skipping feature extraction.")
            return {}

        try:
            input_tensor = self._preprocess_image(image_path_or_obj)
            
            # Call the KerasLayer directly for inference
            output_tensor = self.model(input_tensor)
            feature_vector = output_tensor.numpy()[0]
            
            return {
                "resnet_v2_50_feature_mean": float(np.mean(feature_vector)),
                "resnet_v2_50_feature_std": float(np.std(feature_vector)),
                "resnet_v2_50_feature_max": float(np.max(feature_vector)),
            }
        except Exception as e:
            print(f"Error during ResNet V2 50 (Hub Layer) inference: {e}")
            return {}

import numpy as np
from PIL import Image
import os

try:
    from ai_edge_litert import LiteRT as Interpreter
except ImportError:
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        from tensorflow.lite.python.interpreter import Interpreter

class EfficientNetEngine:
    """
    An engine that uses a real EfficientNet-Lite TFLite model to extract features.
    """
    def __init__(self, model_path="models/efficientnet_lite0.tflite", config=None):
        print("Initializing REAL EfficientNet-Lite Engine...")
        self.model_path = model_path
        self.interpreter = None
        if not os.path.exists(self.model_path):
            print(f"!!! ERROR: Model file not found at {self.model_path} !!!")
            return
        try:
            self.interpreter = Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_height = self.input_details[0]['shape'][1]
            self.input_width = self.input_details[0]['shape'][2]
            print(f"Model {model_path} loaded successfully.")
        except Exception as e:
            print(f"!!! ERROR: Failed to load TFLite model at {self.model_path} !!!")
            print(f"Error: {e}")
            self.interpreter = None

    def _preprocess_image(self, image_path):
        img = Image.open(image_path).convert('RGB')
        img = img.resize((self.input_width, self.input_height))
        # Float model expects float32 input normalized to [0, 1]
        input_data = np.array(img, dtype=np.float32) / 255.0
        input_data = np.expand_dims(input_data, axis=0)
        return input_data

    def extract_features(self, image_path):
        if not self.interpreter:
            return {"effnet_error": "Model not loaded"}

        try:
            input_data = self._preprocess_image(image_path)
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            feature_vector = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            
            return {
                "effnet_feature_mean": float(np.mean(feature_vector)),
                "effnet_feature_std": float(np.std(feature_vector)),
                "effnet_feature_max": float(np.max(feature_vector)),
            }
        except Exception as e:
            print(f"Error during EfficientNet-Lite inference for {image_path}: {e}")
            return {"effnet_error": str(e)}
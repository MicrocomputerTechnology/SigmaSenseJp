
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

class MobileNetV1Engine:
    """
    An engine that uses a real MobileNetV1 TFLite model (non-quantized) to extract features.
    """
    def __init__(self, model_path="models/mobilenet_v1.tflite", config=None):
        print("Initializing REAL MobileNetV1 Engine...")
        self.model_path = model_path
        self.interpreter = None
        if not os.path.exists(self.model_path):
            print(f"!!! ERROR: Model file not found at {self.model_path} !!!")
            print("Please ensure the model has been downloaded manually.")
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

    def _preprocess_image(self, image_data):
        img = image_data.convert('RGB')
        img = img.resize((self.input_width, self.input_height))
        # Quantized model expects uint8 input, not normalized float
        input_data = np.array(img, dtype=np.uint8)
        input_data = np.expand_dims(input_data, axis=0)
        return input_data

    def extract_features(self, image_data):
        if not self.interpreter:
            print(f"MobileNetV1: Model not loaded. Skipping feature extraction.")
            return {}

        try:
            input_data = self._preprocess_image(image_data)
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            feature_vector = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            
            return {
                "mobilenet_v1_feature_mean": float(np.mean(feature_vector)),
                "mobilenet_v1_feature_std": float(np.std(feature_vector)),
                "mobilenet_v1_feature_max": float(np.max(feature_vector)),
            }
        except Exception as e:
            print(f"Error during MobileNetV1 inference: {e}")
            return {}

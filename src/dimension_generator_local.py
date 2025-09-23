
import os
from sigma_image_engines.engine_opencv_legacy import LegacyOpenCVEngine
from sigma_image_engines.engine_efficientnet import EfficientNetEngine
from sigma_image_engines.engine_mobilenet import MobileNetV1Engine
from sigma_image_engines.engine_mobilevit import MobileViTEngine
from sigma_image_engines.engine_resnet import ResNetEngine

class DimensionGenerator:
    """
    Generates a combined vector of semantic dimensions for an image by
    aggregating features from multiple specialized image processing engines.
    """

    def __init__(self, config=None):
        """
        Initializes the generator by loading all available engines.
        """
        print("Initializing Multi-Engine Dimension Generator...")
        self.engines = [
            LegacyOpenCVEngine(),
            EfficientNetEngine(),
            MobileNetV1Engine(),
            MobileViTEngine(),
            ResNetEngine()
        ]
        print(f"{len(self.engines)} engines loaded.")

    def generate_dimensions(self, image_data):
        """
        Generates a comprehensive dimension object for a given image.

        Args:
            image_data (PIL.Image.Image or np.ndarray): The image data (PIL Image or NumPy array).

        Returns:
            dict: A dictionary containing features, provenance, and engine info.
        """
        print(f"--- Generating Dimensions for in-memory image ---")
        
        combined_features = {}
        provenance = {}
        engine_info = {}

        for engine in self.engines:
            engine_name = engine.__class__.__name__
            processed_image_data = None

            # Convert image_data to the format expected by the engine
            if "OpenCV" in engine_name: # OpenCV engines expect NumPy array (BGR)
                if isinstance(image_data, Image.Image):
                    processed_image_data = np.array(image_data.convert('BGR'))
                elif isinstance(image_data, np.ndarray):
                    processed_image_data = image_data # Assume it's already BGR if from OpenCV
                else:
                    print(f"Warning: Unsupported image_data type for OpenCV engine {engine_name}. Skipping.")
                    continue
            else: # TensorFlow engines expect PIL Image
                if isinstance(image_data, np.ndarray):
                    processed_image_data = Image.fromarray(image_data)
                elif isinstance(image_data, Image.Image):
                    processed_image_data = image_data
                else:
                    print(f"Warning: Unsupported image_data type for TensorFlow engine {engine_name}. Skipping.")
                    continue

            try:
                print(f"Querying {engine_name}")
                features = engine.extract_features(processed_image_data)
                if features:
                    combined_features.update(features)
                    # Record the source engine for each feature
                    for feature_key in features.keys():
                        provenance[feature_key] = engine_name
                    print(f"  -> Extracted {len(features)} features.")
                else:
                    print(f"  -> No features extracted.")
                
                # Store engine metadata
                engine_info[engine_name] = {"model": getattr(engine, 'model_path', 'N/A')}

            except Exception as e:
                print(f"Error querying {engine_name}: {e}")
        
        print(f"--- Total Dimensions Generated: {len(combined_features)} ---")
        
        return {
            "features": combined_features,
            "provenance": provenance,
            "engine_info": engine_info
        }

if __name__ == '__main__':
    import cv2
    import numpy as np

    print("--- Running Multi-Engine Dimension Generator ---")
    
    # Create a dummy image for testing
    test_image = "sigma_images/multi_engine_test.png"
    if not os.path.exists("sigma_images"):
        os.makedirs("sigma_images")
    
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    image = cv2.circle(image, (100, 100), 50, (255, 100, 50), -1)
    cv2.imwrite(test_image, image)

    if not os.path.exists(test_image):
        print(f"Test image not found at {test_image}")
    else:
        try:
            generator = DimensionGenerator()
            
            print(f"\n--- Generating dimensions for {test_image} ---")
            result = generator.generate_dimensions(test_image)
            dimensions = result.get("features", {})
            
            if dimensions:
                print("\n--- Combined Dimensions Vector ---")
                for dim, value in dimensions.items():
                    if isinstance(value, float):
                        display_value = f"{value:.4f}"
                    else:
                        display_value = value
                    print(f"  - {dim}: {display_value}")
                
                print("\n--- Provenance ---")
                for feature, engine in result.get("provenance", {}).items():
                    print(f"  - {feature}: {engine}")

            else:
                print("No dimensions were generated.")

        except Exception as e:
            print(f"An error occurred during the test run: {e}")

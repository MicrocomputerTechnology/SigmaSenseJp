
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
import cv2
import json
import time
from PIL import Image
from sigma_image_engines.engine_opencv_legacy import LegacyOpenCVEngine
from sigma_image_engines.engine_mobilenet import MobileNetV1Engine
from sigma_image_engines.engine_mobilevit import MobileViTEngine
from vetra.vetra_llm_core import VetraLLMCore

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
            # EfficientNetEngine(), # Temporarily disabled due to CI loading issues
            MobileNetV1Engine(),
            MobileViTEngine(),
            # ResNetEngine()      # Temporarily disabled due to CI loading issues
        ]
        print(f"{len(self.engines)} engines loaded.")

        # Initialize VetraLLMCore and the path for discovered dimensions
        self.vetra = VetraLLMCore()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.discovered_dims_path = os.path.join(project_root, 'config', 'vector_dimensions_discovered.yaml')

    def generate_dimensions(self, image_path_or_obj):
        """
        Generates a comprehensive dimension object for a given image path or object.

        Args:
            image_path_or_obj (str or PIL.Image): The path to the image file or a PIL Image object.

        Returns:
            dict: A dictionary containing features, provenance, and engine info.
        """
        # Path existence is checked by individual engines if a path is provided.
        image_name = os.path.basename(image_path_or_obj) if isinstance(image_path_or_obj, str) else "in-memory_image"
        print(f"--- Generating Dimensions for {image_name} ---")
        
        combined_features = {}
        provenance = {}
        engine_info = {}

        for engine in self.engines:
            engine_name = engine.__class__.__name__
            try:
                print(f"Querying {engine_name}")
                features = engine.extract_features(image_path_or_obj)
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
        
        # --- Autonomous Discovery of New Dimensions ---
        if self._is_unknown(combined_features):
            print("\n🔬 Unknown characteristics detected. Attempting to propose a new dimension...")
            self._propose_and_save_new_dimension(combined_features)

        return {
            "features": combined_features,
            "provenance": provenance,
            "engine_info": engine_info
        }

    def _is_unknown(self, features: dict) -> bool:
        """
        Determines if a feature set is \"unknown\".
        Simple heuristic: if the average absolute value of all features is low.
        """
        if not features:
            return False
        
        values = np.array(list(features.values()))
        # If all dimensions show low values
        if np.mean(np.abs(values)) < 0.05: # Threshold may need adjustment
            print(f"  - Unknownness Assessment: All features have low activity (Avg. Abs. Value: {np.mean(np.abs(values)):.4f})")
            return True
            
        return False

    def _propose_and_save_new_dimension(self, features: dict):
        """
        Asks Vetra to propose a new dimension and saves it to a file.
        """
        print("  - Asking Vetra to propose a new dimension...")
        new_dim = self.vetra.propose_new_dimension(features)

        if not new_dim or "error" in new_dim or "id" not in new_dim:
            print(f"  - Failure: Could not get a valid new dimension proposal. ({new_dim.get('error', 'Invalid format')})")
            return

        print(f"  - Proposed new dimension: {new_dim.get('name_ja', 'N/A')} (id: {new_dim['id']})")

        # Load existing discovered dimensions
        if os.path.exists(self.discovered_dims_path):
            try:
                with open(self.discovered_dims_path, 'r', encoding='utf-8') as f:
                    discovered_dims = yaml.safe_load(f) or []
            except (IOError, yaml.YAMLError) as e:
                print(f"  - Warning: Could not load existing discovered dimensions file. Starting fresh. Error: {e}")
                discovered_dims = []
        else:
            discovered_dims = []
            
        # Check for duplicates
        if any(d.get('id') == new_dim['id'] for d in discovered_dims if isinstance(d, dict)):
            print(f"  - Skip: Dimension '{new_dim['id']}' already exists.")
            return

        # Append the new dimension
        discovered_dims.append(new_dim)

        # Write back to the file
        try:
            with open(self.discovered_dims_path, 'w', encoding='utf-8') as f:
                yaml.dump(discovered_dims, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"  - Success: Saved new dimension to {self.discovered_dims_path}")
        except Exception as e:
            print(f"  - Failure: Error saving the new dimension: {e}")


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

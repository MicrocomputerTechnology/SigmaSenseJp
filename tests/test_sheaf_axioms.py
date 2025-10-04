import unittest
import numpy as np
from PIL import Image
import os
import sys
import shutil
import cv2 # Import cv2
import json
import yaml


# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigmasense.sigma_sense import SigmaSense
from src.sigmasense.dimension_loader import DimensionLoader
from src.sigmasense.sigma_database_loader import load_sigma_database
from src.sigmasense.build_database import build_database
from src.sigmasense.world_model import WorldModel


# ... (imports) ...

class TestSheafAxiomsSimplified(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test class once."""
        print("\n--- Setting up Simplified Sheaf Axioms Test ---")
        
        import tempfile
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, 'test_db.sqlite')
        
        # 1. Create two separate, non-overlapping images in BGR format
        cls.red_image_path = os.path.join(cls.temp_dir, 'red_square.png')
        img_red_rgb = Image.new('RGB', (100, 100), 'red')
        img_red_np = np.array(img_red_rgb)
        img_red_bgr = cv2.cvtColor(img_red_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite(cls.red_image_path, img_red_bgr)
        
        cls.blue_image_path = os.path.join(cls.temp_dir, 'blue_square.png')
        img_blue_rgb = Image.new('RGB', (100, 100), 'blue')
        img_blue_np = np.array(img_blue_rgb)
        img_blue_bgr = cv2.cvtColor(img_blue_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite(cls.blue_image_path, img_blue_bgr)
        
        # 2. Build a database from these images using merged dimension files
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        dimension_files = [
            "config/vector_dimensions_mobile.yaml",
            "config/vector_dimensions_custom_ai.json"
        ]
        config_paths = [os.path.join(project_root, path) for path in dimension_files]

        all_dims = []
        for path in config_paths:
            if not os.path.exists(path):
                print(f"Warning: Test dimension file not found: {path}")
                continue
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    all_dims.extend(json.load(f))
                elif path.endswith(('.yaml', '.yml')):
                    all_dims.extend(yaml.safe_load(f))
        
        cls.merged_config_path = os.path.join(cls.temp_dir, 'merged_dimensions.json')
        with open(cls.merged_config_path, 'w', encoding='utf-8') as f:
            json.dump(all_dims, f)

        build_database(db_path=cls.db_path, img_dir=cls.temp_dir, dimension_config_path=cls.merged_config_path)

        # 3. Load the database and instantiate SigmaSense
        cls.loader = DimensionLoader(paths=[cls.merged_config_path])
        database, ids, vectors, _ = load_sigma_database(cls.db_path)
        
        # --- Test-specific WorldModel --- #
        cls.test_wm_path = os.path.join(cls.temp_dir, 'test_sheaf_axioms_wm.sqlite')
        cls.test_wm = WorldModel(db_path=cls.test_wm_path)

        cls.sigma = SigmaSense(database, ids, vectors, [], dimension_loader=cls.loader, world_model=cls.test_wm)
        cls.ids = ids
        cls.vectors = vectors
        print("SigmaSense instance created with test database.")

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class once."""
        cls.test_wm.close()
        shutil.rmtree(cls.temp_dir)
        print(f"\nCleaned up temporary directory: {cls.temp_dir}")

    def test_red_square_detection(self):
        """Tests if a solid red image is correctly identified as red."""
        print("\n--- Testing Red Square Detection ---")
        
        # Find the vector for the red image (id is filename without extension)
        idx = self.ids.index('red_square')
        v_red = self.vectors[idx]
        
        d_hue_index = self.loader.get_index('dominant_hue_of_shapes')
        self.assertIsNotNone(d_hue_index, "dominant_hue_of_shapes dimension not found.")
        
        hue = v_red[d_hue_index]
        print(f"Asserting Red: Hue={hue:.2f}")
        # Hue for red is around 0 or 1 in a normalized scale
        self.assertTrue(hue < 0.1 or hue > 0.9, f"Red square's hue should be near 0 or 1, but was {hue}")
        print("OK: Red square correctly identified.")

    def test_blue_square_detection(self):
        """Tests if a solid blue image is correctly identified as blue."""
        print("\n--- Testing Blue Square Detection ---")
        
        # Find the vector for the blue image (id is filename without extension)
        idx = self.ids.index('blue_square')
        v_blue = self.vectors[idx]
        
        d_hue_index = self.loader.get_index('dominant_hue_of_shapes')
        self.assertIsNotNone(d_hue_index, "dominant_hue_of_shapes dimension not found.")
        
        hue = v_blue[d_hue_index]
        print(f"Asserting Blue: Hue={hue:.2f}")
        # Hue for blue is around 0.67 in a normalized scale
        self.assertGreater(hue, 0.6, f"Blue square's hue should be > 0.6, but was {hue}")
        self.assertLess(hue, 0.75, f"Blue square's hue should be < 0.75, but was {hue}")
        print("OK: Blue square correctly identified.")

if __name__ == '__main__':
    unittest.main()

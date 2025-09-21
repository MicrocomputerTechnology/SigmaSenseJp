import unittest
import numpy as np
from PIL import Image, ImageDraw
import os
import sys
from unittest.mock import MagicMock

# --- Mock modules to bypass heavy dependencies ---
# This is to avoid installing spacy, ginza, etc. just for this test.
sys.modules['spacy'] = MagicMock()
sys.modules['ginza'] = MagicMock()
sys.modules['ja_ginza'] = MagicMock()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_sense import SigmaSense
from src.sheaf_analyzer import SheafAnalyzer
from src.dimension_loader import DimensionLoader
from src.sigma_database_loader import load_sigma_database

class TestSheafAxioms(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test class once.
        This involves creating a temporary database for the test.
        """
        from src.build_database import build_database, IMG_DIR, DB_PATH
        import tempfile

        print("\n--- Setting up TestSheafAxioms ---" )
        cls.temp_dir = tempfile.TemporaryDirectory()
        
        # Override the default image and db paths for the test
        build_database.IMG_DIR = os.path.join(cls.temp_dir.name, "images")
        build_database.DB_PATH = os.path.join(cls.temp_dir.name, "test_db.json")
        os.makedirs(build_database.IMG_DIR)

        # Create dummy images to build the database
        img_red = Image.new('RGB', (100, 100), 'white')
        draw_red = ImageDraw.Draw(img_red)
        draw_red.rectangle([10, 10, 90, 90], fill='red')
        img_red.save(os.path.join(build_database.IMG_DIR, 'red_square.png'))

        img_blue = Image.new('RGB', (100, 100), 'white')
        draw_blue = ImageDraw.Draw(img_blue)
        draw_blue.rectangle([10, 10, 90, 90], fill='blue')
        img_blue.save(os.path.join(build_database.IMG_DIR, 'blue_square.png'))

        img_purple = Image.new('RGB', (100, 100), 'white')
        draw_purple = ImageDraw.Draw(img_purple)
        draw_purple.rectangle([10, 10, 90, 90], fill='purple')
        img_purple.save(os.path.join(build_database.IMG_DIR, 'purple_square.png'))

        # Build the database
        build_database()

        # 2. Instantiate a real SigmaSense instance
        cls.loader = DimensionLoader()
        db_path = build_database.DB_PATH
        database, ids, vectors = load_sigma_database(db_path)
        cls.sigma = SigmaSense(database, ids, vectors, dimension_loader=cls.loader)
        print("SigmaSense instance created successfully.")

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class once.
        Deletes the temporary directory.
        """
        cls.temp_dir.cleanup()
        print(f"\nCleaned up temp directory: {cls.temp_dir.name}")

    def test_color_detection(self):
        dim_map = self.loader.get_dimension_map()
        try:
            d_hue = dim_map['dominant_hue_of_shapes']
        except KeyError as e:
            self.fail(f"This test requires the 'dominant_hue_of_shapes' dimension. Missing: {e}")

        # --- Red ---
        result_red = self.sigma.process_experience(os.path.join(self.temp_dir.name, "images", 'red_square.png'))
        v_red = np.array(result_red['vector'])
        self.assertTrue(v_red[d_hue] < 0.1 or v_red[d_hue] > 0.9, f"Red square hue should be < 0.1 or > 0.9, but was {v_red[d_hue]}")

        # --- Blue ---
        result_blue = self.sigma.process_experience(os.path.join(self.temp_dir.name, "images", 'blue_square.png'))
        v_blue = np.array(result_blue['vector'])
        self.assertTrue(0.6 < v_blue[d_hue] < 0.75, f"Blue square hue should be between 0.6 and 0.75, but was {v_blue[d_hue]}")
        
        # --- Purple ---
        result_purple = self.sigma.process_experience(os.path.join(self.temp_dir.name, "images", 'purple_square.png'))
        v_purple = np.array(result_purple['vector'])
        self.assertTrue(v_purple[d_hue] > 0.75, f"Purple square hue should be > 0.75, but was {v_purple[d_hue]}")


if __name__ == '__main__':
    unittest.main()

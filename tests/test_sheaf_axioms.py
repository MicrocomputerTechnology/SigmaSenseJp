import unittest
import numpy as np
from PIL import Image, ImageDraw
import os
import sys
import shutil # Import shutil for rmtree
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
from src.build_database import build_database # Import build_database directly

class TestSheafAxioms(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test class once.
        This involves creating a synthetic image and instantiating a real SigmaSense.
        """
        print("\n--- Setting up TestSheafAxioms ---" )
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(cls.test_data_dir, exist_ok=True)
        import tempfile
        import shutil
        
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_image_path = os.path.join(cls.temp_dir.name, 'temp_sheaf_test_image.png')
        cls.test_db_path = os.path.join(cls.temp_dir.name, 'test_db.json')
        
        # 1. Create a synthetic image with overlapping colored squares
        img = Image.new('RGB', (200, 150), 'white')
        draw = ImageDraw.Draw(img)
        # U1: Red square
        draw.rectangle([10, 10, 110, 110], fill='red')
        # U2: Blue square
        draw.rectangle([80, 40, 180, 140], fill='blue')
        # Overlap U12 is implicitly purple
        img.save(cls.test_image_path)
        print(f"Created synthetic image at: {cls.test_image_path}")

        # Create a dummy image to build the database
        dummy_img = Image.new('RGB', (10, 10), 'green')
        dummy_img.save(os.path.join(cls.temp_dir.name, 'dummy.png'))

        # Build the database in the temporary directory
        # Need to pass output_path and img_dir to build_database
        build_database(db_path=cls.test_db_path, img_dir=cls.temp_dir.name)

        # 2. Instantiate a real SigmaSense instance
        cls.loader = DimensionLoader()
        database, ids, vectors = load_sigma_database(cls.test_db_path)
        cls.sigma = SigmaSense(database, ids, vectors, dimension_loader=cls.loader)
        print("SigmaSense instance created successfully.")

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class once.
        Deletes the temporary directory.
        """
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)
        shutil.rmtree(cls.temp_dir.name) # Use cls.temp_dir.name for TemporaryDirectory cleanup
        print(f"\nCleaned up test data directory: {cls.temp_dir.name}")


    def test_gluing_semantic_consistency(self):
        """
        Tests a weaker, semantic version of the gluing axiom.
        Checks if the feature vectors of overlapping regions are semantically consistent.
        """
        # 1. Define the regions (open sets)
        # U1: Red square region
        r1 = (10, 10, 100, 100)
        # U2: Blue square region
        r2 = (80, 40, 100, 100)
        # U12: Overlap region (purple)
        r12 = (80, 40, 30, 70) # Calculated intersection of r1 and r2

        # 2. Instantiate SheafAnalyzer
        analyzer = SheafAnalyzer(self.test_image_path, self.sigma)

        # 3. Get feature vectors for each region
        print("\n--- Testing Gluing Semantic Consistency ---")
        print("Extracting vector for Red region (U1)...")
        v1 = analyzer._get_feature_vector_for_region(r1)
        print("Extracting vector for Blue region (U2)...")
        v2 = analyzer._get_feature_vector_for_region(r2)
        print("Extracting vector for Purple overlap (U12)...")
        v12 = analyzer._get_feature_vector_for_region(r12)

        self.assertIsNotNone(v1, "Vector for U1 should not be None")
        self.assertIsNotNone(v2, "Vector for U2 should not be None")
        self.assertIsNotNone(v12, "Vector for U12 should not be None")

        # 4. Get index for the dominant hue dimension
        try:
            d_hue = self.loader.get_index('dominant_hue_of_shapes')
            if d_hue is None:
                raise KeyError("'dominant_hue_of_shapes' not found in dimension map.")
        except KeyError as e:
            self.fail(f"This test requires the 'dominant_hue_of_shapes' dimension. Missing: {e}")

        # 5. Assert semantic consistency (the "Mathematical Test")
        # In OpenCV HSV, Hue is 0-179. Red is ~0, Blue is ~120, Purple is ~150.
        # Normalized to 0-1: Red ~0, Blue ~0.67, Purple ~0.83
        
        print(f"Asserting semantic consistency for Red vector (v1): Hue={v1[d_hue]:.2f}")
        self.assertTrue(v1[d_hue] < 0.1 or v1[d_hue] > 0.9, "Red region vector should have a hue value corresponding to red.")

        print(f"Asserting semantic consistency for Blue vector (v2): Hue={v2[d_hue]:.2f}")
        self.assertGreater(v2[d_hue], 0.6, "Blue region vector should have a hue value corresponding to blue.")
        self.assertLess(v2[d_hue], 0.75, "Blue region vector should have a hue value corresponding to blue.")
        
        print(f"Asserting semantic consistency for Purple vector (v12): Hue={v12[d_hue]:.2f}")
        self.assertGreater(v12[d_hue], 0.75, "Purple overlap should have a hue value corresponding to purple/magenta.")
        
        print("\nOK: Semantic consistency holds for overlapping regions.")

if __name__ == '__main__':
    unittest.main()
import unittest
import numpy as np
from PIL import Image
import os
import sys
import shutil
import tempfile
from unittest.mock import MagicMock

# --- Mock modules to bypass heavy dependencies ---
sys.modules['spacy'] = MagicMock()
sys.modules['ginza'] = MagicMock()
sys.modules['ja_ginza'] = MagicMock()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_sense import SigmaSense
from src.dimension_loader import DimensionLoader
from src.sigma_database_loader import load_sigma_database
from src.build_database import build_database
from src.image_transformer import identity as identity_transform

class TestCategoryTheory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a real SigmaSense instance for testing functor properties."""
        print("\n--- Setting up TestCategoryTheory ---")
        cls.temp_dir = os.path.join(os.path.dirname(__file__), 'temp_test_cat_dir')
        os.makedirs(cls.temp_dir, exist_ok=True)

        cls.db_path = os.path.join(cls.temp_dir, 'test_db.json')
        
        # Create a dummy image to ensure the database can be built
        dummy_img_path = os.path.join(cls.temp_dir, 'dummy.png')
        Image.new('RGB', (10, 10), 'green').save(dummy_img_path)

        # Build a database using the dummy image
        build_database(db_path=cls.db_path, img_dir=cls.temp_dir)

        # Load the database and instantiate SigmaSense
        cls.loader = DimensionLoader()
        database, ids, vectors = load_sigma_database(cls.db_path)
        cls.sigma = SigmaSense(database, ids, vectors, dimension_loader=cls.loader)
        print("SigmaSense instance created for category theory tests.")

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory."""
        shutil.rmtree(cls.temp_dir)
        print(f"\nCleaned up temporary directory: {cls.temp_dir}")

    def test_functor_preserves_identity(self):
        """
        Tests if the SigmaSense functor preserves identity morphisms.
        F(id_A) should be equal to id_F(A), which means applying an identity
        image transformation should not change the resulting vector.
        """
        # 1. Arrange: Get the vector for the original image
        image_path = 'sigma_images/circle_center.jpg'
        self.assertTrue(os.path.exists(image_path), f"Test image not found at {image_path}")
        
        original_result = self.sigma.process_experience(image_path)
        self.assertIsNotNone(original_result, "Processing the original image failed.")
        vector_original = np.array(original_result['vector'])

        # 2. Act: Apply the identity transform and get the new vector
        pil_image = Image.open(image_path).convert('RGB')
        transformed_image = identity_transform(pil_image)

        # Save the transformed image to a temporary file to get a path
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False, dir=self.temp_dir) as tmp:
            transformed_image.save(tmp.name, "PNG")
            transformed_image_path = tmp.name

        transformed_result = self.sigma.process_experience(transformed_image_path)
        os.remove(transformed_image_path) # Clean up the temporary file

        self.assertIsNotNone(transformed_result, "Processing the transformed image failed.")
        vector_transformed = np.array(transformed_result['vector'])

        # 3. Assert: The vectors should be identical
        self.assertTrue(np.array_equal(vector_original, vector_transformed),
                        "The vector should not change after applying an identity transformation.")
        print("OK: Functor correctly preserves identity morphism.")

if __name__ == '__main__':
    unittest.main()

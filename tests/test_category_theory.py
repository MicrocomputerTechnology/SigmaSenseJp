import unittest
import numpy as np
from PIL import Image, ImageOps
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
from src.sigma_functor import SigmaFunctor
from src.vector_transforms import VectorTransforms

class TestCategoryTheory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a real SigmaSense instance for testing functor properties."""
        print("\n--- Setting up TestCategoryTheory ---")
        
        # Skip tests if models are not present
        model_paths = [
            'models/efficientnet_lite0.tflite',
            'models/mobilenet_v1.tflite',
            'models/mobilevit-tensorflow2-xxs-1k-256-v1',
            'models/resnet_v2_50_saved_model'
        ]
        if not all(os.path.exists(p) for p in model_paths):
            raise unittest.SkipTest("Skipping category theory tests: ML models not found.")

        cls.temp_dir = os.path.join(os.path.dirname(__file__), 'temp_test_cat_dir')
        os.makedirs(cls.temp_dir, exist_ok=True)

        cls.db_path = os.path.join(cls.temp_dir, 'test_db.json')
        
        # Create a dummy image to ensure the database can be built
        dummy_img_path = os.path.join(cls.temp_dir, 'dummy.png')
        Image.new('RGB', (10, 10), 'green').save(dummy_img_path)

        # Build a database using the dummy image
        build_database(db_path=cls.db_path, img_dir=cls.temp_dir, dimension_config_path="config/vector_dimensions_mobile.yaml")

        # Load the database and instantiate SigmaSense
        cls.loader = DimensionLoader()
        database, ids, vectors, _ = load_sigma_database(cls.db_path)
        cls.sigma = SigmaSense(database, ids, vectors, [], dimension_loader=cls.loader)
        print("SigmaSense instance created for category theory tests.")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the temporary directory.
        """
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

class TestFunctoriality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n--- Setting up TestFunctoriality ---")
        cls.temp_dir = os.path.join(os.path.dirname(__file__), 'temp_test_functor_dir')
        os.makedirs(cls.temp_dir, exist_ok=True)

        cls.db_path = os.path.join(cls.temp_dir, 'test_db_functor.json')
        
        # Create a dummy image to ensure the database can be built
        dummy_img_path = os.path.join(cls.temp_dir, 'dummy_functor.png')
        Image.new('RGB', (10, 10), 'red').save(dummy_img_path)

        # Build a database using the dummy image
        build_database(db_path=cls.db_path, img_dir=cls.temp_dir, dimension_config_path="config/vector_dimensions_mobile.yaml")

        # Load the database and instantiate SigmaSense
        cls.loader = DimensionLoader()
        database, ids, vectors, _ = load_sigma_database(cls.db_path)
        cls.sigma = SigmaSense(database, ids, vectors, [], dimension_loader=cls.loader)
        vector_transforms_instance = VectorTransforms(cls.loader)
        cls.sigma_functor = SigmaFunctor(vector_transforms_instance, cls.sigma)
        print("SigmaSense and SigmaFunctor instances created for functoriality tests.")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the temporary directory.
        """
        shutil.rmtree(cls.temp_dir)
        print(f"\nCleaned up temporary directory: {cls.temp_dir}")

    @staticmethod
    def _rotate_hue_image_transform(pil_image, angle_deg):
        """
        Rotates the hue channel of a PIL image.
        PIL's ImageOps.colorize can be used for hue shifts, but it's complex.
        A simpler approach for testing is to convert to HSV, shift H, convert back.
        """
        hsv_image = pil_image.convert('HSV')
        h, s, v = hsv_image.split()

        # Shift hue (0-255 for PIL, corresponds to 0-360 degrees)
        # OpenCV hue is 0-179 for 0-360 degrees.
        # Let's assume a direct mapping for simplicity in this test.
        # If angle_deg is 90, it means 90 degrees shift.
        # PIL hue is 0-255, so 255 corresponds to 360 degrees.
        # Shift amount in PIL units = angle_deg * (255 / 360)
        
        # For simplicity, let's just use Image.eval for hue shift
        # This is a very basic hue shift, might not be perfectly accurate for all cases.
        # The goal is to create a *corresponding* vector transform.
        shifted_h = h.point(lambda i: (i + int(angle_deg * (255/360))) % 256)
        
        return Image.merge('HSV', (shifted_h, s, v)).convert('RGB')

    @staticmethod
    def _scale_image_transform(pil_image, scale_factor):
        """
        Scales a PIL image.
        """
        new_size = (int(pil_image.width * scale_factor), int(pil_image.height * scale_factor))
        return pil_image.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def _translate_image_transform(pil_image, dx, dy):
        """
        Translates a PIL image.
        """
        return pil_image.transform(pil_image.size, Image.AFFINE, (1, 0, dx, 0, 1, dy))

    def test_hue_rotation_functoriality(self):
        """
        Tests if the hue rotation image transform corresponds to the hue rotation vector transform.
        F(g(x)) approx (F_g)(F(x))
        """
        image_path = 'sigma_images/circle_center_red.jpg' # A red circle for clear hue
        self.assertTrue(os.path.exists(image_path), f"Test image not found at {image_path}")

        angle_deg = 90 # Rotate hue by 90 degrees

        # Image transform function (g)
        image_transform_func = lambda img: self._rotate_hue_image_transform(img, angle_deg)

        # Vector transform function name (F_g)
        vector_transform_func_name = "rotate_hue_vector_transform"

        diff_norm, is_consistent, vec_after_g, expected_vec_after = \
            self.sigma_functor.check_functoriality(image_path, image_transform_func, vector_transform_func_name, angle_deg)

        print(f"\n--- Hue Rotation Functoriality Test ---")
        print(f"Diff Norm: {diff_norm}")
        print(f"Is Consistent: {is_consistent}")
        print(f"Vector after image transform (F(g(x))): {vec_after_g}")
        print(f"Expected vector after vector transform ((F_g)(F(x))): {expected_vec_after}")

        self.assertTrue(is_consistent, "Hue rotation functoriality check failed: not consistent.")
        self.assertLess(diff_norm, 0.1, "Hue rotation functoriality check failed: difference too large.")

    def test_scale_functoriality(self):
        """
        Tests if image scaling corresponds to vector scaling.
        """
        image_path = 'sigma_images/square_left.jpg' # A simple shape for clear scaling
        self.assertTrue(os.path.exists(image_path), f"Test image not found at {image_path}")

        scale_factor = 0.5 # Scale image to half size

        # Image transform function (g)
        image_transform_func = lambda img: self._scale_image_transform(img, scale_factor)

        # Vector transform function name (F_g)
        vector_transform_func_name = "scale_vector_transform"

        diff_norm, is_consistent, vec_after_g, expected_vec_after = \
            self.sigma_functor.check_functoriality(image_path, image_transform_func, vector_transform_func_name, scale_factor)

        print(f"\n--- Scale Functoriality Test ---")
        print(f"Diff Norm: {diff_norm}")
        print(f"Is Consistent: {is_consistent}")
        print(f"Vector after image transform (F(g(x))): {vec_after_g}")
        print(f"Expected vector after vector transform ((F_g)(F(x))): {expected_vec_after}")

        self.assertTrue(is_consistent, "Scale functoriality check failed: not consistent.")
        self.assertLess(diff_norm, 0.1, "Scale functoriality check failed: difference too large.")

    def test_translation_functoriality(self):
        """
        Tests if image translation corresponds to vector translation.
        """
        image_path = 'sigma_images/square_left.jpg' # A simple shape for clear translation
        self.assertTrue(os.path.exists(image_path), f"Test image not found at {image_path}")

        dx, dy = 10, 20 # Translate image by 10 pixels right, 20 pixels down

        # Image transform function (g)
        image_transform_func = lambda img: self._translate_image_transform(img, dx, dy)

        # Vector transform function name (F_g)
        vector_transform_func_name = "translate_vector_transform"

        diff_norm, is_consistent, vec_after_g, expected_vec_after = \
            self.sigma_functor.check_functoriality(image_path, image_transform_func, vector_transform_func_name, dx, dy)

        print(f"\n--- Translation Functoriality Test ---")
        print(f"Diff Norm: {diff_norm}")
        print(f"Is Consistent: {is_consistent}")
        print(f"Vector after image transform (F(g(x))): {vec_after_g}")
        print(f"Expected vector after vector transform ((F_g)(F(x))): {expected_vec_after}")

        self.assertTrue(is_consistent, "Translation functoriality check failed: not consistent.")
        self.assertLess(diff_norm, 0.1, "Translation functoriality check failed: difference too large.")

if __name__ == '__main__':
    unittest.main()

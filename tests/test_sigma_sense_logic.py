import unittest
import numpy as np
from unittest.mock import MagicMock
import cv2

class TestSigmaSenseLogicIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a test environment for SigmaSense with a dedicated test WorldModel."""
        # 1. Create a temporary WorldModel for this test
        self.test_db_path = 'test_logic_wm.sqlite'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.test_wm = WorldModel(db_path=self.test_db_path)
        self.test_wm.add_node('is_dog')
        self.test_wm.add_node('animal')
        self.test_wm.add_edge('is_dog', 'animal', 'is_a')

        # 2. Instantiate DimensionLoader with the specific test file
        self.test_dim_loader = DimensionLoader(paths=['config/vector_dimensions_test_logic.json'])

        # 3. Create a mock for the dimension generator
        self.mock_generator = MagicMock()

        # 4. Create dummy database parameters for the vector DB part
        self.dummy_db = {}
        self.dummy_ids = []
        self.dummy_vectors = np.array([])
        self.dummy_layers = []

        # 5. Instantiate SigmaSense, injecting the test WorldModel, loader, and mock generator
        self.sigma_sense = SigmaSense(
            self.dummy_db, 
            self.dummy_ids, 
            self.dummy_vectors,
            self.dummy_layers,
            generator=self.mock_generator,
            dimension_loader=self.test_dim_loader,
            world_model=self.test_wm  # Inject the test WorldModel
        )

    def tearDown(self):
        """Clean up the temporary database file."""
        self.test_wm.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

class TestProbabilisticImageComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = OpenCVEngine()
        cls.test_dir = "./test_images_probabilistic"
        os.makedirs(cls.test_dir, exist_ok=True)

        # Create test images
        cls.red_square_path = os.path.join(cls.test_dir, "red_square.png")
        cls.blue_square_path = os.path.join(cls.test_dir, "blue_square.png")
        cls.similar_red_square_path = os.path.join(cls.test_dir, "similar_red_square.png")

        cls._create_colored_square(cls.red_square_path, (0, 0, 255)) # BGR for OpenCV
        cls._create_colored_square(cls.blue_square_path, (255, 0, 0)) # BGR for OpenCV
        cls._create_colored_square(cls.similar_red_square_path, (0, 0, 250)) # Slightly different red

    @classmethod
    def tearDownClass(cls):
        # Clean up test images and directory
        if os.path.exists(cls.red_square_path):
            os.remove(cls.red_square_path)
        if os.path.exists(cls.blue_square_path):
            os.remove(cls.blue_square_path)
        if os.path.exists(cls.similar_red_square_path):
            os.remove(cls.similar_red_square_path)
        if os.path.exists(cls.test_dir):
            os.rmdir(cls.test_dir)

    @staticmethod
    def _create_colored_square(path, color, size=50):
        img = np.full((size, size, 3), color, dtype=np.uint8)
        cv2.imwrite(path, img)

    def test_different_colors_high_divergence(self):
        """
        Tests that images with very different colors have high probabilistic divergence.
        """
        results = self.engine.compare_images_probabilistically(self.red_square_path, self.blue_square_path)
        
        # Expect high divergence for hue histograms
        self.assertGreater(results["h_hist_kl_divergence"], 1.0, "KL divergence for different hues should be high.")
        self.assertGreater(results["h_hist_wasserstein_distance"], 10.0, "Wasserstein distance for different hues should be high.")

    def test_similar_colors_low_divergence(self):
        """
        Tests that images with very similar colors have low probabilistic divergence.
        """
        results = self.engine.compare_images_probabilistically(self.red_square_path, self.similar_red_square_path)

        # Expect low divergence for hue histograms
        self.assertLess(results["h_hist_kl_divergence"], 0.1, "KL divergence for similar hues should be low.")
        self.assertLess(results["h_hist_wasserstein_distance"], 5.0, "Wasserstein distance for similar hues should be low.")

if __name__ == '__main__':
    import os
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    sys.path.insert(0, os.path.join(project_root, 'sigma_image_engines'))

    os.environ['DIMENSION_FILE_PATH'] = 'config/vector_dimensions_test_logic.json'
    from src.sigmasense.sigma_sense import SigmaSense
    from src.sigmasense.dimension_loader import DimensionLoader
    from engine_opencv import OpenCVEngine

    from src.sigmasense.world_model import WorldModel
    unittest.main()
import unittest
import numpy as np
import os
from unittest.mock import MagicMock
import cv2

import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'sigma_image_engines'))# Set the dimension loader to use our test file BEFORE importing sigma_sense
os.environ['DIMENSION_FILE_PATH'] = 'config/vector_dimensions_test_logic.json'
from src.sigma_sense import SigmaSense
from src.dimension_loader import DimensionLoader
from engine_opencv import OpenCVEngine

class TestSigmaSenseLogicIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a test environment for SigmaSense."""
        # 1. Instantiate DimensionLoader with the specific test file FIRST
        self.test_dim_loader = DimensionLoader(paths=['config/vector_dimensions_test_logic.json'])

        # 2. Create a mock for the dimension generator
        self.mock_generator = MagicMock()

        # 3. Create dummy database parameters
        self.dummy_db = {}
        self.dummy_ids = []
        self.dummy_vectors = np.array([])

        # 4. Instantiate SigmaSense, injecting the test loader and mock generator
        self.sigma_sense = SigmaSense(
            self.dummy_db, 
            self.dummy_ids, 
            self.dummy_vectors,
            generator=self.mock_generator,
            dimension_loader=self.test_dim_loader
        )

    def test_dog_inference_and_logic(self):
        """
        Test if providing 'is_dog' feature correctly infers 'is_animal'
        and evaluates the 'is_canine' logical rule.
        """
        print("\n--- Running test_dog_inference_and_logic ---")
        
        # 1. Define the mock return value for the generator
        mock_features = {
            "is_dog": 1.0,
            "is_wolf": 0.0
        }
        mock_generation_result = {
            "features": mock_features,
            "provenance": {k: "mock_engine" for k in mock_features.keys()},
            "engine_info": {"mock_engine": {"model": "mock"}}
        }
        self.mock_generator.generate_dimensions.return_value = mock_generation_result
        print(f"Mock input features: {mock_features}")

        # 2. Call the process_experience method with a dummy path
        result = self.sigma_sense.process_experience("dummy_dog_image.jpg")

        # 3. Verify the results
        final_vector = result['vector']
        dimensions = self.test_dim_loader.get_dimensions()
        dim_map = {dim['id']: i for i, dim in enumerate(dimensions)}

        print(f"Final vector: {final_vector}")

        # Check that 'is_dog' is 1.0
        self.assertEqual(final_vector[dim_map['is_dog']], 1.0)
        print(f"Assertion PASSED: 'is_dog' is {final_vector[dim_map['is_dog']]}")

        # Check that 'animal' was inferred to be 1.0 by the SymbolicReasoner
        self.assertTrue('animal' in dim_map, "Dimension 'animal' not found in test dimensions.")
        self.assertEqual(final_vector[dim_map['animal']], 1.0)
        print(f"Assertion PASSED: 'animal' was inferred as {final_vector[dim_map['animal']]}")

        # Check that 'is_canine' was evaluated to 1.0 by the LogicalExpressionEngine
        self.assertTrue('is_canine' in dim_map, "Dimension 'is_canine' not found in test dimensions.")
        self.assertEqual(final_vector[dim_map['is_canine']], 1.0)
        print(f"Assertion PASSED: 'is_canine' was logically evaluated as {final_vector[dim_map['is_canine']]}")
        
        # Check that the intent narrative was generated
        self.assertTrue('intent_narrative' in result)
        self.assertIsInstance(result['intent_narrative'], str)
        # The old test checked for "照合根拠の語り", the new one for "判断意図の語り"
        self.assertIn("判断意図の語り", result['intent_narrative'])
        print(f"Assertion PASSED: 'intent_narrative' was generated.")
        print("\n--- Generated Narrative ---")
        print(result['intent_narrative'])
        
        print("--- Test finished successfully ---")

    def test_find_best_match_with_different_metrics(self):
        """
        Tests that _find_best_match correctly identifies the best match
        using different similarity metrics (cosine, KL divergence, Wasserstein).
        """
        print("\n--- Running test_find_best_match_with_different_metrics ---")

        # 1. Create a dummy database for SigmaSense
        # These vectors are designed to be easily comparable for different metrics
        # They are normalized to sum to 1 to act as probability distributions for KL/Wasserstein
        # For cosine, the magnitude also matters, but relative values are key.
        target_vec = np.array([0.1, 0.2, 0.7], dtype=np.float32)
        db_vec_a = np.array([0.1, 0.2, 0.7], dtype=np.float32) # Identical to target
        db_vec_b = np.array([0.7, 0.2, 0.1], dtype=np.float32) # Very different
        db_vec_c = np.array([0.2, 0.3, 0.5], dtype=np.float32) # Somewhat similar

        dummy_ids = ["vec_a", "vec_b", "vec_c"]
        dummy_vectors = np.array([db_vec_a, db_vec_b, db_vec_c], dtype=np.float32)
        dummy_weights = np.array([1.0, 1.0, 1.0], dtype=np.float32) # All dimensions equally important

        # Temporarily override sigma_sense's database for this test
        original_vectors = self.sigma_sense.vectors
        original_ids = self.sigma_sense.ids
        original_weights = self.sigma_sense.weights

        self.sigma_sense.vectors = dummy_vectors
        self.sigma_sense.ids = dummy_ids
        self.sigma_sense.weights = dummy_weights

        # 2. Test with 'cosine' metric
        best_id_cosine, score_cosine, _ = self.sigma_sense._find_best_match(target_vec, metric='cosine')
        print(f"Cosine: Best match = {best_id_cosine}, Score = {score_cosine:.4f}")
        self.assertEqual(best_id_cosine, "vec_a")
        self.assertAlmostEqual(score_cosine, 1.0, places=4) # Identical vectors should have cosine similarity of 1

        # 3. Test with 'kl_divergence' metric
        # For KL, identical distributions should yield max similarity (1.0)
        best_id_kl, score_kl, _ = self.sigma_sense._find_best_match(target_vec, metric='kl_divergence')
        print(f"KL Divergence: Best match = {best_id_kl}, Score = {score_kl:.4f}")
        self.assertEqual(best_id_kl, "vec_a")
        self.assertAlmostEqual(score_kl, 1.0, places=4) # Identical distributions should have 0 KL div, so 1/(1+0)=1 similarity

        # 4. Test with 'wasserstein' metric
        # For Wasserstein, identical distributions should yield max similarity (1.0)
        best_id_wasserstein, score_wasserstein, _ = self.sigma_sense._find_best_match(target_vec, metric='wasserstein')
        print(f"Wasserstein: Best match = {best_id_wasserstein}, Score = {score_wasserstein:.4f}")
        self.assertEqual(best_id_wasserstein, "vec_a")
        self.assertAlmostEqual(score_wasserstein, 1.0, places=4) # Identical distributions should have 0 Wasserstein dist, so 1/(1+0)=1 similarity

        # Restore original sigma_sense database
        self.sigma_sense.vectors = original_vectors
        self.sigma_sense.ids = original_ids
        self.sigma_sense.weights = original_weights
        print("--- Test finished successfully ---")

    def test_publication_gatekeeper_uses_saphiel_config(self):
        """
        Test that PublicationGatekeeper uses forbidden_keywords from saphiel_mission_profile.json.
        """
        print("\n--- Running test_publication_gatekeeper_uses_saphiel_config ---")

        # 1. Define a narrative that contains a forbidden keyword
        self.sigma_sense.intent_justifier.justify_decision = MagicMock(return_value="これは機密データに関する報告です。")
        self.sigma_sense.meta_narrator.narrate_growth = MagicMock(return_value="システムは順調に成長しています。")

        # 2. Call the process_experience method with a dummy path
        result = self.sigma_sense.process_experience("dummy_image.jpg")

        # 3. Assert that the narrative was blocked
        self.assertFalse(result["ethics_passed"])
        self.assertIn("Blocked. Narrative conflicts with mission profile (found confidential keyword: '機密データ')", result["ethics_log"][-1])
        self.assertIn("[REDACTED BY AEGIS", result["intent_narrative"])
        print("--- Test finished successfully ---")

    def tearDown(self):
        """Clean up environment variables."""
        # No need to manage env vars anymore
        pass

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
    unittest.main()
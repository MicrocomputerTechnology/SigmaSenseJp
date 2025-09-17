import unittest
import numpy as np
import os
from unittest.mock import MagicMock

# Set the dimension loader to use our test file BEFORE importing sigma_sense
os.environ['DIMENSION_FILE_PATH'] = 'vector_dimensions_test_logic.json'
from sigma_sense import SigmaSense
from dimension_loader import DimensionLoader

class TestSigmaSenseLogicIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a test environment for SigmaSense."""
        # 1. Instantiate DimensionLoader with the specific test file FIRST
        self.test_dim_loader = DimensionLoader(selia_path='vector_dimensions_test_logic.json')

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

        # 2. Call the match method with a dummy path, disabling reconstruction
        result = self.sigma_sense.match("dummy_dog_image.jpg", reconstruct=False)

        # 3. Verify the results
        final_vector = result['vector']
        dimensions = self.test_dim_loader.get_dimensions()
        dim_map = {dim['id']: i for i, dim in enumerate(dimensions)}

        print(f"Final vector: {final_vector}")

        # Check that 'is_dog' is 1.0
        self.assertEqual(final_vector[dim_map['is_dog']], 1.0)
        print(f"Assertion PASSED: 'is_dog' is {final_vector[dim_map['is_dog']]}")

        # Check that 'is_animal' was inferred to be 1.0 by the SymbolicReasoner
        self.assertTrue('is_animal' in dim_map, "Dimension 'is_animal' not found in test dimensions.")
        self.assertEqual(final_vector[dim_map['is_animal']], 1.0)
        print(f"Assertion PASSED: 'is_animal' was inferred as {final_vector[dim_map['is_animal']]}")

        # Check that 'is_canine' was evaluated to 1.0 by the LogicalExpressionEngine
        self.assertTrue('is_canine' in dim_map, "Dimension 'is_canine' not found in test dimensions.")
        self.assertEqual(final_vector[dim_map['is_canine']], 1.0)
        print(f"Assertion PASSED: 'is_canine' was logically evaluated as {final_vector[dim_map['is_canine']]}")
        
        # Check that the narrative justification was generated
        self.assertTrue('narrative_justification' in result)
        self.assertIsInstance(result['narrative_justification'], str)
        self.assertIn("照合根拠の語り", result['narrative_justification'])
        print(f"Assertion PASSED: 'narrative_justification' was generated.")
        print("\n--- Generated Narrative ---")
        print(result['narrative_justification'])
        
        print("--- Test finished successfully ---")

    def tearDown(self):
        """Clean up environment variables."""
        # No need to manage env vars anymore
        pass


if __name__ == '__main__':
    unittest.main()

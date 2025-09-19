import unittest
import numpy as np
import os
from unittest.mock import MagicMock

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the dimension loader to use our test file BEFORE importing sigma_sense
os.environ['DIMENSION_FILE_PATH'] = 'config/vector_dimensions_test_logic.json'
from src.sigma_sense import SigmaSense
from src.dimension_loader import DimensionLoader

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

    def tearDown(self):
        """Clean up environment variables."""
        # No need to manage env vars anymore
        pass


if __name__ == '__main__':
    unittest.main()

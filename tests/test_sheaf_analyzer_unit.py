
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigmasense.sheaf_analyzer import SheafAnalyzer

class TestSheafAnalyzerUnit(unittest.TestCase):
    """
    Unit tests for the SheafAnalyzer focusing on its mathematical logic (gluing)
    without the overhead of real model inference.
    """

    def setUp(self):
        """Create a dummy image file for tests."""
        self.dummy_image_path = 'dummy_test_image.png'
        Image.new('RGB', (100, 100), 'white').save(self.dummy_image_path)

    def tearDown(self):
        """Remove the dummy image file."""
        if os.path.exists(self.dummy_image_path):
            os.remove(self.dummy_image_path)

    @patch('src.sigmasense.sheaf_analyzer.structure_detector.extract_structure_features')
    def test_glue_logic_with_mocked_inference(self, mock_extract_features):
        """
        Tests the glue() method's weighted average calculation using mocked data
        to ensure the core mathematical logic is correct and fast.
        """
        print("\n--- Running Unit Test: SheafAnalyzer Gluing Logic ---")

        # 1. Define mock data
        # Mock regions that the structure_detector would find
        mock_regions = [
            {'x': 0, 'y': 0, 'w': 10, 'h': 10},  # Area = 100
            {'x': 20, 'y': 20, 'w': 20, 'h': 20} # Area = 400
        ]
        mock_extract_features.return_value = mock_regions

        # Mock vectors that SigmaSense would generate for each region
        vector1 = np.array([0.1, 0.2, 0.3])
        vector2 = np.array([0.4, 0.5, 0.6])
        
        # The mock process_experience will return vector1 for the first region, vector2 for the second
        mock_sigma_instance = MagicMock()
        mock_sigma_instance.process_experience.side_effect = [
            {'vector': vector1},
            {'vector': vector2}
        ]

        # 2. Calculate the expected result manually
        area1 = 10 * 10
        area2 = 20 * 20
        total_area = area1 + area2
        expected_glued_vector = ((vector1 * area1) + (vector2 * area2)) / total_area
        print(f"Expected Glued Vector: {expected_glued_vector}")

        # 3. Run the SheafAnalyzer with the mocked dependencies
        # We patch check_gluing_condition to always return True to isolate the glue logic
        with patch.object(SheafAnalyzer, 'check_gluing_condition', return_value=True):
            analyzer = SheafAnalyzer(self.dummy_image_path, mock_sigma_instance)
            # assign_local_data will use the mocked functions
            analyzer.assign_local_data() 
            glued_vector = analyzer.glue()

        print(f"Actual Glued Vector:   {glued_vector}")
        
        # 4. Assert that the actual result matches the expected calculation
        self.assertIsNotNone(glued_vector)
        self.assertTrue(np.allclose(glued_vector, expected_glued_vector),
                        "The glued vector does not match the expected weighted average.")
        
        print("OK: SheafAnalyzer's glue logic is correct.")

if __name__ == '__main__':
    unittest.main()

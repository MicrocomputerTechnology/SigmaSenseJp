
import unittest
import numpy as np
from PIL import Image
import os

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sheaf_analyzer import SheafAnalyzer

# --- Mock Objects for Testing ---

class MockSigmaSense:
    """ A mock of the SigmaSense class for testing purposes. """
    def process_experience(self, image_path):
        """ 
        Returns a consistent, predefined vector regardless of the input image path.
        This simulates a scenario where all regions are perfectly consistent.
        """
        # The actual content of the vector doesn't matter, only its consistency.
        return {'vector': np.array([0.1, 0.2, 0.3, 0.4, 0.5])}

# --- Test Cases ---

class TestSheafAnalyzer(unittest.TestCase):

    def setUp(self):
        """ Set up for the tests. """
        # Create a dummy image file for the analyzer to use.
        # We use a real image from the project to ensure file paths are correct.
        self.test_image_path = os.path.join(os.path.dirname(__file__), '..', 'sigma_images', 'multi_object.jpg')
        
        # If the test image doesn't exist, create a placeholder
        if not os.path.exists(self.test_image_path):
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.test_image_path), exist_ok=True)
            # Create a simple black image
            dummy_img = Image.new('RGB', (100, 100), 'black')
            dummy_img.save(self.test_image_path)

        self.mock_sigma = MockSigmaSense()
        self.analyzer = SheafAnalyzer(self.test_image_path, self.mock_sigma)

    def test_01_assign_local_data(self):
        """ Test that local data is assigned correctly. """
        # The structure_detector should find regions in the test image.
        self.analyzer.assign_local_data()
        # We expect at least one region to be found.
        self.assertGreater(len(self.analyzer.local_data), 0, "Should find at least one region.")
        # Check if the vectors are assigned.
        first_vector = next(iter(self.analyzer.local_data.values()))
        self.assertIsNotNone(first_vector, "Vector should not be None.")
        self.assertTrue(np.allclose(first_vector, self.mock_sigma.process_experience(None)['vector']), "Vector should match the mock's output.")

    def test_02_check_gluing_condition_consistent(self):
        """ 
        Test the gluing condition check with a consistent mock.
        Since the mock always returns the same vector, the check should pass.
        """
        # The analyzer will use the mock, which always returns the same vector.
        # Therefore, any overlapping regions should be perfectly consistent.
        is_consistent = self.analyzer.check_gluing_condition()
        self.assertTrue(is_consistent, "Gluing condition should pass with a consistent mock.")

    def test_03_glue_with_consistent_data(self):
        """ Test the glue() method with consistent data. """
        # Since the gluing check will pass, glue() should return a vector.
        global_vector = self.analyzer.glue()
        self.assertIsNotNone(global_vector, "Global vector should not be None after gluing.")
        # The global vector should be the same as the mock vector since it's an average of identical vectors.
        self.assertTrue(np.allclose(global_vector, self.mock_sigma.process_experience(None)['vector']), "Global vector should match the mock vector.")

if __name__ == '__main__':
    unittest.main()

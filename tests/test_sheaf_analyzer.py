
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
    def process_experience(self, image_data):
        """
        Returns a consistent, predefined vector regardless of the input image data.
        This simulates a scenario where all regions are perfectly consistent.
        """
        # The actual content of the vector doesn't matter, only its consistency.
        return {'vector': np.array([0.1, 0.2, 0.3, 0.4, 0.5])}

# --- Test Cases ---

class TestSheafAnalyzer(unittest.TestCase):

    def setUp(self):
        """
        Set up for the tests.
        """
        # Create a dummy in-memory image (NumPy array)
        self.dummy_image_data = np.zeros((100, 100, 3), dtype=np.uint8)
        self.dummy_image_data[:, :, 0] = 255 # Blue channel

        self.mock_sigma = MockSigmaSense()
        self.analyzer = SheafAnalyzer(self.dummy_image_data, self.mock_sigma)

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

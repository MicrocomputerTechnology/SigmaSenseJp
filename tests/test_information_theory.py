import unittest
import numpy as np
import sys
import os

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from information_metrics import compute_entropy

class TestInformationTheory(unittest.TestCase):

    def test_zero_entropy_for_deterministic_distribution(self):
        """
        Tests that a deterministic distribution (only one non-zero element) has zero entropy.
        This is a fundamental property of Shannon Entropy.
        """
        # Arrange
        deterministic_vector = [0, 0, 5, 0, 0]

        # Act
        entropy = compute_entropy(deterministic_vector)

        # Assert
        self.assertEqual(entropy, 0.0, "A deterministic vector should have zero entropy.")

    def test_maximum_entropy_for_uniform_distribution(self):
        """
        Tests that a uniform distribution has maximum possible entropy.
        For a vector of size n, max entropy is log2(n).
        """
        # Arrange
        uniform_vector = [1, 1, 1, 1]
        n = len(uniform_vector)
        expected_max_entropy = np.log2(n)

        # Act
        entropy = compute_entropy(uniform_vector)

        # Assert
        self.assertAlmostEqual(entropy, expected_max_entropy, places=4, msg="A uniform vector should have maximum entropy.")

    def test_entropy_for_known_distribution(self):
        """
        Tests the entropy calculation for a known, non-trivial probability distribution.
        P = [0.5, 0.25, 0.25]
        Entropy = -(0.5*log2(0.5) + 0.25*log2(0.25) + 0.25*log2(0.25)) = 1.5
        """
        # Arrange
        known_vector = [2, 1, 1] # Corresponds to probabilities [0.5, 0.25, 0.25]
        expected_entropy = 1.5

        # Act
        entropy = compute_entropy(known_vector)

        # Assert
        self.assertAlmostEqual(entropy, expected_entropy, places=4, msg="Entropy for P=[0.5, 0.25, 0.25] should be 1.5.")
        
    def test_empty_vector(self):
        """
        Tests that an empty vector or a vector of zeros results in zero entropy.
        """
        # Arrange
        empty_vector = []
        zero_vector = [0, 0, 0]

        # Act
        entropy_empty = compute_entropy(empty_vector)
        entropy_zero = compute_entropy(zero_vector)

        # Assert
        self.assertEqual(entropy_empty, 0.0, "An empty vector should have zero entropy.")
        self.assertEqual(entropy_zero, 0.0, "A zero vector should have zero entropy.")

if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np
import sys
import os

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from information_metrics import compute_entropy, compute_kl_divergence

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

class TestKLDivergence(unittest.TestCase):

    def test_divergence_of_self_is_zero(self):
        """
        Tests that the KL divergence of a distribution with itself is zero. D_KL(P || P) = 0.
        """
        # Arrange
        p = [0.1, 0.2, 0.7]

        # Act
        divergence = compute_kl_divergence(p, p)

        # Assert
        self.assertAlmostEqual(divergence, 0.0, places=4, msg="KL divergence of a distribution with itself should be zero.")

    def test_divergence_is_non_negative(self):
        """
        Tests that KL divergence is always non-negative. D_KL(P || Q) >= 0.
        """
        # Arrange
        p = [0.1, 0.2, 0.7]
        q = [0.7, 0.2, 0.1]

        # Act
        divergence = compute_kl_divergence(p, q)

        # Assert
        self.assertGreaterEqual(divergence, 0.0, "KL divergence should be non-negative.")

    def test_divergence_is_not_symmetric(self):
        """
        Tests that KL divergence is not symmetric. D_KL(P || Q) != D_KL(Q || P).
        """
        # Arrange
        p = [0.2, 0.8]
        q = [0.6, 0.4]

        # Act
        div_pq = compute_kl_divergence(p, q)
        div_qp = compute_kl_divergence(q, p)

        # Assert
        self.assertNotAlmostEqual(div_pq, div_qp, msg="KL divergence should not be symmetric.")

    def test_divergence_with_known_values(self):
        """
        Tests KL divergence for a known case.
        P = [0.5, 0.5], Q = [0.25, 0.75]
        D_KL(P || Q) = 0.5*log2(0.5/0.25) + 0.5*log2(0.5/0.75) = 0.5*log2(2) + 0.5*log2(2/3) = 0.5*1 + 0.5*(log2(2)-log2(3)) = 0.5 + 0.5*(1-1.58496) = 0.2075
        """
        # Arrange
        p = [0.5, 0.5]
        q = [0.25, 0.75]
        expected_divergence = 0.2075

        # Act
        divergence = compute_kl_divergence(p, q)

        # Assert
        self.assertAlmostEqual(divergence, expected_divergence, places=4, msg="KL divergence for known P, Q is incorrect.")

    def test_divergence_with_zeros(self):
        """
        Tests that divergence calculation is stable when zeros are present.
        """
        # Arrange
        p = [0.5, 0.5, 0]
        q = [0.25, 0.25, 0.5]

        # Act
        divergence = compute_kl_divergence(p, q)

        # Assert
        self.assertTrue(np.isfinite(divergence), "Divergence should be a finite number even with zeros.")

if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np
import sys
import os
import collections

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from information_metrics import compute_entropy, compute_kl_divergence, compute_wasserstein_distance, compute_mutual_information, to_probability_distribution

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
        D_KL(P || Q) = 0.5*log2(0.5/0.25) + 0.5*log2(0.5/0.75) = 0.5*1 + 0.5*(log2(2)-log2(3)) = 0.5 + 0.5*(1-1.58496) = 0.2075
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

class TestWassersteinDistance(unittest.TestCase):

    def test_distance_of_self_is_zero(self):
        """
        Tests that the Wasserstein distance of a distribution to itself is zero.
        """
        # Arrange
        p = [1, 2, 3, 4, 5]

        # Act
        distance = compute_wasserstein_distance(p, p)

        # Assert
        self.assertAlmostEqual(distance, 0.0, places=4, msg="Distance to self should be zero.")

    def test_distance_is_symmetric(self):
        """
        Tests that Wasserstein distance is symmetric. d(u, v) = d(v, u).
        """
        # Arrange
        u = [1, 2, 5]
        v = [3, 4, 6]

        # Act
        dist_uv = compute_wasserstein_distance(u, v)
        dist_vu = compute_wasserstein_distance(v, u)

        # Assert
        self.assertAlmostEqual(dist_uv, dist_vu, places=4, msg="Distance should be symmetric.")

    def test_distance_with_known_values(self):
        """
        Tests the distance between two simple, known distributions.
        The distance between a distribution at point 0 and one at point 2 should be 2.
        """
        # Arrange
        u_values = [0]
        v_values = [2]
        expected_distance = 2.0

        # Act
        distance = compute_wasserstein_distance(u_values, v_values)

        # Assert
        self.assertAlmostEqual(distance, expected_distance, places=4, msg="Distance between [0] and [2] should be 2.")

    def test_translation_invariance(self):
        """
        Tests that the distance is the same if both distributions are shifted.
        d([0], [2]) should be equal to d([10], [12]).
        """
        # Arrange
        u1 = [0]
        v1 = [2]
        u2 = [10]
        v2 = [12]

        # Act
        dist1 = compute_wasserstein_distance(u1, v1)
        dist2 = compute_wasserstein_distance(u2, v2)

        # Assert
        self.assertAlmostEqual(dist1, dist2, places=4, msg="Distance should be invariant to translation.")

class TestMutualInformation(unittest.TestCase):

    def test_mutual_information_of_independent_variables_is_zero(self):
        """
        Tests that mutual information is zero for independent variables.
        """
        # Arrange
        x = [0, 0, 1, 1, 0, 0, 1, 1]
        y = [0, 1, 0, 1, 0, 1, 0, 1] # Independent of x

        # Act
        mi = compute_mutual_information(x, y)

        # Assert
        self.assertAlmostEqual(mi, 0.0, places=4, msg="MI for independent variables should be zero.")

    def test_mutual_information_of_variable_with_itself_is_entropy(self):
        """
        Tests that mutual information of a variable with itself is its entropy.
        I(X; X) = H(X).
        """
        # Arrange
        x = [0, 0, 1, 1, 2, 2]
        # Calculate H(X) manually for comparison
        # P(0)=1/3, P(1)=1/3, P(2)=1/3. H(X) = -3 * (1/3 * log2(1/3)) = log2(3) approx 1.58496
        counts = collections.Counter(x)
        total_elements = sum(counts.values())
        probabilities = [count / total_elements for count in counts.values()]
        expected_entropy = compute_entropy(probabilities) # Use our own entropy function for consistency

        # Act
        mi = compute_mutual_information(x, x)

        # Assert
        self.assertAlmostEqual(mi, expected_entropy, places=4, msg="MI(X;X) should be H(X).")

    def test_mutual_information_is_non_negative(self):
        """
        Tests that mutual information is always non-negative.
        """
        # Arrange
        x = [0, 0, 1, 1]
        y = [0, 1, 0, 1]

        # Act
        mi = compute_mutual_information(x, y)

        # Assert
        self.assertGreaterEqual(mi, 0.0, "Mutual information should be non-negative.")

    def test_mutual_information_with_known_values(self):
        """
        Tests mutual information for a known case.
        X = [0, 0, 1, 1]
        Y = [0, 1, 0, 1]
        P(X=0,Y=0)=0.25, P(X=0,Y=1)=0.25, P(X=1,Y=0)=0.25, P(X=1,Y=1)=0.25
        P(X=0)=0.5, P(X=1)=0.5
        P(Y=0)=0.5, P(Y=1)=0.5
        H(X) = 1, H(Y) = 1, H(X,Y) = 2
        I(X;Y) = H(X) + H(Y) - H(X,Y) = 1 + 1 - 2 = 0
        """
        # Arrange
        x = [0, 0, 1, 1]
        y = [0, 1, 0, 1]
        expected_mi = 0.0 # For this specific independent case

        # Act
        mi = compute_mutual_information(x, y)

        # Assert
        self.assertAlmostEqual(mi, expected_mi, places=4, msg="MI for known independent variables is incorrect.")

class TestProbabilityDistributionConversion(unittest.TestCase):

    def test_basic_conversion(self):
        """
        Tests basic conversion of a simple array to a probability distribution.
        """
        # Arrange
        data = [1, 2, 2, 3, 3, 3]
        # Expected: hist = [1, 2, 3] for bins=3 (or similar depending on bin edges)
        # Normalized: [1/6, 2/6, 3/6] = [0.1667, 0.3333, 0.5]
        # With default bins=10, it will be more spread out.
        # Let's use a fixed bin range for predictability.
        # Data range is 1 to 3. Bins: [1, 1.2, 1.4, ..., 3]
        # For simplicity, let's test with data that falls neatly into bins.
        data = [1, 1, 2, 2, 3, 3] # 2 of each
        # If bins=3, and range is 1-3, then bins could be [1, 1.66, 2.33, 3]
        # 1s fall into first bin, 2s into second, 3s into third.
        # hist = [2, 2, 2]
        # prob_dist = [1/3, 1/3, 1/3]
        expected_dist = np.array([1/3, 1/3, 1/3])

        # Act
        prob_dist = to_probability_distribution(data, bins=3) # Specify bins for predictability

        # Assert
        np.testing.assert_allclose(prob_dist, expected_dist, rtol=1e-4, atol=1e-4,
                                   err_msg="Basic conversion to probability distribution is incorrect.")

    def test_sum_of_probabilities_is_one(self):
        """
        Tests that the sum of the probabilities in the resulting distribution is 1.
        """
        # Arrange
        data = np.random.rand(100)

        # Act
        prob_dist = to_probability_distribution(data)

        # Assert
        self.assertAlmostEqual(np.sum(prob_dist), 1.0, places=6,
                               msg="Sum of probabilities should be 1.")

    def test_empty_data_handling(self):
        """
        Tests that an empty data array results in an empty probability distribution.
        """
        # Arrange
        data = []

        # Act
        prob_dist = to_probability_distribution(data)

        # Assert
        self.assertEqual(len(prob_dist), 0, "Empty data should result in an empty distribution.")

    def test_different_bin_numbers(self):
        """
        Tests conversion with a different number of bins.
        """
        # Arrange
        data = [1, 1, 1, 2, 2, 3, 4, 4, 4, 4]
        # With bins=4, and data range 1-4, each bin gets 1 unit.
        # hist = [3, 2, 1, 4]
        # prob_dist = [0.3, 0.2, 0.1, 0.4]
        expected_dist = np.array([0.3, 0.2, 0.1, 0.4])

        # Act
        prob_dist = to_probability_distribution(data, bins=4)

        # Assert
        np.testing.assert_allclose(prob_dist, expected_dist, rtol=1e-4, atol=1e-4,
                                   err_msg="Conversion with different bins is incorrect.")

if __name__ == '__main__':
    unittest.main()
import numpy as np
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.information_metrics import compute_entropy, mutual_information, kl_divergence
from src.reconstruction_trigger import should_trigger_reconstruction

def run_tests():
    """
    Runs all information theory related unit tests.
    """
    print("--- Starting Information Theory Functions Test ---")

    # --- Test Data ---
    vec_uniform = np.array([0.25, 0.25, 0.25, 0.25])
    vec_sparse = np.array([0.9, 0.1, 0.0, 0.0])
    vec_identical_1 = np.random.rand(100)
    vec_identical_2 = vec_identical_1.copy()
    vec_random = np.random.rand(100)
    dist_p = np.array([0.1, 0.9])
    dist_q = np.array([0.8, 0.2])

    # --- 1. Entropy Test ---
    print("\n[1. Entropy Test]")
    entropy_uniform = compute_entropy(vec_uniform)
    entropy_sparse = compute_entropy(vec_sparse)
    print(f"Entropy (Uniform): {entropy_uniform}")
    print(f"Entropy (Sparse): {entropy_sparse}")
    assert entropy_uniform > entropy_sparse, "Test failed: Uniform entropy should be greater than sparse entropy."
    print("OK: Uniform entropy is correctly higher than sparse entropy.")

    # --- 2. Mutual Information Test ---
    print("\n[2. Mutual Information Test]")
    mi_identical = mutual_information(vec_identical_1, vec_identical_2)
    mi_random = mutual_information(vec_identical_1, vec_random)
    print(f"Mutual Information (Identical): {mi_identical}")
    print(f"Mutual Information (Random): {mi_random}")
    assert mi_identical > mi_random, "Test failed: MI for identical vectors should be higher than for random vectors."
    print("OK: Mutual information for identical vectors is correctly higher.")

    # --- 3. KL Divergence Test ---
    print("\n[3. KL Divergence Test]")
    kl_same = kl_divergence(dist_p, dist_p)
    kl_different = kl_divergence(dist_p, dist_q)
    print(f"KL Divergence (P || P): {kl_same}")
    print(f"KL Divergence (P || Q): {kl_different}")
    assert kl_different > kl_same, "Test failed: KL divergence for different distributions should be greater."
    print("OK: KL divergence for different distributions is correctly higher.")

    # --- 4. Reconstruction Trigger Test ---
    print("\n[4. Reconstruction Trigger Test]")
    # Test Case 4.1: Low entropy trigger
    low_entropy_vector = [0.99, 0.01, 0, 0, 0, 0, 0, 0, 0, 0]
    trigger_entropy = should_trigger_reconstruction(low_entropy_vector, threshold_entropy=1.0)
    print(f"Trigger on low entropy (entropy={compute_entropy(low_entropy_vector)}): {trigger_entropy}")
    assert trigger_entropy is True, "Test failed: Should trigger for low entropy."
    print("OK: Triggered correctly on low entropy.")

    # Test Case 4.2: High KL divergence trigger
    p_vec = [0.1, 0.2, 0.7]
    q_vec = [0.7, 0.2, 0.1]
    trigger_kl = should_trigger_reconstruction(p_vec, vector_q=q_vec, threshold_kl=0.5)
    print(f"Trigger on high KL divergence (KL={kl_divergence(p_vec, q_vec)}): {trigger_kl}")
    assert trigger_kl is True, "Test failed: Should trigger for high KL divergence."
    print("OK: Triggered correctly on high KL divergence.")

    # Test Case 4.3: No trigger
    high_entropy_vector = [0.25, 0.25, 0.25, 0.25]
    no_trigger_entropy = should_trigger_reconstruction(high_entropy_vector, threshold_entropy=1.0)
    print(f"No trigger on high entropy (entropy={compute_entropy(high_entropy_vector)}): {not no_trigger_entropy}")
    assert no_trigger_entropy is False, "Test failed: Should not trigger for high entropy."
    print("OK: Did not trigger on high entropy as expected.")

    print("\n--- All Information Theory Tests Passed Successfully! ---")

if __name__ == '__main__':
    run_tests()

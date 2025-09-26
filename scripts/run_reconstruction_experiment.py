import os
import sys
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_loader import ConfigLoader
from src.reconstruction_trigger import ReconstructionTrigger

def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

def run_experiment():
    """Runs a series of tests to demonstrate the ReconstructionTrigger."""
    print_header("Reconstruction Trigger Experiment")

    # 1. Load Configuration
    print("1. Loading configuration...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    config_loader = ConfigLoader(config_dir)
    trigger_config = config_loader.get_config('reconstruction_trigger_profile') or {}
    print(f"  - Trigger thresholds loaded: Entropy < {trigger_config.get('threshold_entropy', 2.5)}, KL-Divergence > {trigger_config.get('threshold_kl', 1.0)}")

    # 2. Initialize ReconstructionTrigger
    print("\n2. Initializing ReconstructionTrigger...")
    trigger = ReconstructionTrigger(config=trigger_config) # Assuming constructor is refactored to take config object

    # 3. Define Test Vectors
    print("\n3. Defining test vectors...")
    # Low entropy vector (sparse, should trigger)
    vector_low_entropy = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # High entropy vector (uniform, should not trigger)
    vector_high_entropy = [0.1] * 10
    # Two nearly identical vectors (low KL divergence)
    vector_p1 = [0.1, 0.2, 0.7, 0.0]
    vector_q1 = [0.11, 0.22, 0.67, 0.0]
    # Two very different vectors (high KL divergence, should trigger)
    vector_p2 = [0.1, 0.8, 0.1, 0.0]
    vector_q2 = [0.8, 0.1, 0.1, 0.0]
    print("  - Defined: vector_low_entropy, vector_high_entropy, two similar vectors (p1, q1), two different vectors (p2, q2).")

    # 4. Run Experiments
    print("\n4. Running trigger checks...")
    
    # Test Case 1: Low Entropy
    should_trigger_low_entropy = trigger.should_trigger_reconstruction(vector_low_entropy)
    print(f"  - Test Case 1 (Low Entropy Vector): Triggered -> {should_trigger_low_entropy}")
    assert should_trigger_low_entropy is True

    # Test Case 2: High Entropy
    should_trigger_high_entropy = trigger.should_trigger_reconstruction(vector_high_entropy)
    print(f"  - Test Case 2 (High Entropy Vector): Triggered -> {should_trigger_high_entropy}")
    assert should_trigger_high_entropy is False

    # Test Case 3: Low KL-Divergence
    should_trigger_low_kl = trigger.should_trigger_reconstruction(vector_p1, vector_q1)
    print(f"  - Test Case 3 (Similar Vectors): Triggered -> {should_trigger_low_kl}")
    assert should_trigger_low_kl is False

    # Test Case 4: High KL-Divergence
    should_trigger_high_kl = trigger.should_trigger_reconstruction(vector_p2, vector_q2)
    print(f"  - Test Case 4 (Different Vectors): Triggered -> {should_trigger_high_kl}")
    assert should_trigger_high_kl is True

    print("\nExperiment finished successfully.")

if __name__ == "__main__":
    run_experiment()

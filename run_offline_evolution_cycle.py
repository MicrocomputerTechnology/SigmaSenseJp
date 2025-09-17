
import os
import yaml
import numpy as np
from sigma_local_core import SigmaLocalCore
from dimension_generator_local import DimensionGeneratorLocal
from dimension_optimizer import DimensionOptimizer

def print_header(title):
    bar = "="*60
    print(f"\n{bar}\n=== {title.upper()} ===\n{bar}")

def reset_config_file(config_path, optimized_path):
    """Resets the config files for a clean, repeatable simulation."""
    print_header("Resetting Configuration to Initial State")
    initial_config = {
        'symmetry_score': {'description': 'Measures symmetry based on Hu Moments.', 'method': '...', 'weight': 0.8, 'parameters': []},
        'edge_density': {'description': 'Calculates the density of edges.', 'method': '...', 'weight': 0.6, 'parameters': []},
        'gaze_curvature': {'description': 'Approximates the curvature of a dominant line.', 'method': '...', 'weight': 0.5, 'parameters': []}
    }
    with open(config_path, 'w') as f:
        yaml.dump(initial_config, f, sort_keys=False)
    if os.path.exists(optimized_path):
        os.remove(optimized_path)
    print(f"'{config_path}' has been reset.\nRemoved old '{optimized_path}' if it existed.")

if __name__ == '__main__':
    CONFIG_PATH = "vector_dimensions_mobile.yaml"
    OPTIMIZED_CONFIG_PATH = "vector_dimensions_mobile_optimized.yaml"
    
    IMG_CIRCLE = "sigma_images/circle_center.jpg"
    IMG_CAT = "sigma_images/cat_01.jpg"
    IMG_NEW_PHENOMENON = "sigma_images/pentagon_center_blue.jpg"

    if not all(os.path.exists(p) for p in [IMG_CIRCLE, IMG_CAT, IMG_NEW_PHENOMENON]):
        print("\nERROR: One or more test images are missing. Aborting simulation.")
        exit()

    reset_config_file(CONFIG_PATH, OPTIMIZED_CONFIG_PATH)

    # === CYCLE 1: BASELINE COMPARISON ===
    print_header("Cycle 1: Baseline Comparison (Before Evolution)")
    core_v1 = SigmaLocalCore(config_path=CONFIG_PATH)
    result_baseline = core_v1.compare_images(IMG_CIRCLE, IMG_CAT)
    if not result_baseline: exit()
    print(f"  -> Similarity (Circle vs Cat): {result_baseline['similarity_score']:.4f}")

    # === CYCLE 2: DISCOVERING NEW DIMENSION ===
    print_header("Cycle 2: Encountering a New Phenomenon")
    generator = DimensionGeneratorLocal(config_path=CONFIG_PATH)
    discovered = generator.discover_new_dimension(IMG_NEW_PHENOMENON)
    if discovered: print(f"Vetra's vocabulary has expanded with the '{discovered}' dimension.")
    else: print("Vetra did not discover any new dimensions.")

    # === CYCLE 3: LEARNING FROM FEEDBACK ===
    print_header("Cycle 3: Learning from Feedback")
    optimizer = DimensionOptimizer(config_path=CONFIG_PATH)
    vec_circle = generator.generate_vector(IMG_CIRCLE)
    vec_cat = generator.generate_vector(IMG_CAT)
    # Create a slightly noisy version of the circle vector for the 'match' case
    vec_circle_noisy = {k: v + np.random.uniform(-0.05, 0.05) for k, v in vec_circle.items()}

    feedback_data = [
        {'vector1': vec_circle, 'vector2': vec_circle_noisy, 'label': 'match'},
        {'vector1': vec_circle, 'vector2': vec_cat, 'label': 'no_match'}
    ]
    print("Providing feedback: (Circle vs Noisy Circle) -> match, (Circle vs Cat) -> no_match")
    optimized_weights = optimizer.optimize(feedback_data)
    optimizer.save_config(output_path=OPTIMIZED_CONFIG_PATH)
    print("Vetra has adjusted its dimension weights.")

    # === CYCLE 4: POST-EVOLUTION COMPARISON ===
    print_header("Cycle 4: Post-Evolution Comparison")
    if not os.path.exists(OPTIMIZED_CONFIG_PATH): 
        print("Optimized config not found.")
    else:
        core_v2 = SigmaLocalCore(config_path=OPTIMIZED_CONFIG_PATH)
        result_evolved = core_v2.compare_images(IMG_CIRCLE, IMG_CAT)
        if result_evolved:
            print(f"\n  -> Similarity (Circle vs Cat) BEFORE evolution: {result_baseline['similarity_score']:.4f}")
            print(f"  -> Similarity (Circle vs Cat) AFTER evolution:  {result_evolved['similarity_score']:.4f}")
            change = result_evolved['similarity_score'] - result_baseline['similarity_score']
            print(f"  -> Change: {change:+.4f}")
            if change < -0.01:
                print("  -> \033[92mSUCCESS: The system has learned to better distinguish the subjects.\033[0m")
            else:
                print("  -> NOTE: The system's understanding shifted.")

    print_header("Offline Evolution Cycle Complete")

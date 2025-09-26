import os
import yaml
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.sigma_local_core import SigmaLocalCore
from src.dimension_generator_local import DimensionGenerator
from src.dimension_optimizer import DimensionOptimizer
from src.dimension_suggester import DimensionSuggester

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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')

    CONFIG_PATH = os.path.join(config_dir, "vector_dimensions_mobile.yaml")
    OPTIMIZED_CONFIG_PATH = os.path.join(config_dir, "vector_dimensions_mobile_optimized.yaml")
    
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

    # === CYCLE 2: DISCOVERING NEW DIMENSION (via Suggester) ===
    print_header("Cycle 2: Encountering a New Phenomenon")
    generator = DimensionGenerator()
    suggester = DimensionSuggester()
    print(f"Analyzing new phenomenon: {os.path.basename(IMG_NEW_PHENOMENON)}")
    new_phenomenon_dims = generator.generate_dimensions(IMG_NEW_PHENOMENON)
    suggestions = suggester.suggest(new_phenomenon_dims['features'])
    if suggestions:
        print("Vetra has new suggestions based on the phenomenon:")
        for sug in suggestions:
            print(f"  - Suggestion: {sug['name']} ({sug['reason']})")
    else:
        print("Vetra did not discover any new dimensions.")

    # === CYCLE 3: LEARNING FROM FEEDBACK ===
    print_header("Cycle 3: Learning from Feedback")
    # Load the config from the YAML file to pass to the optimizer
    with open(CONFIG_PATH, 'r') as f:
        optimizer_config = yaml.safe_load(f)
    optimizer = DimensionOptimizer(config=optimizer_config)
    print("Generating vectors for feedback using current architecture...")
    vec_circle = generator.generate_dimensions(IMG_CIRCLE)['features']
    vec_cat = generator.generate_dimensions(IMG_CAT)['features']
    
    initial_dims = optimizer.current_weights.keys()
    vec_circle_filtered = {k: vec_circle.get(k, 0.0) for k in initial_dims}
    vec_cat_filtered = {k: vec_cat.get(k, 0.0) for k in initial_dims}
    vec_circle_noisy = {k: v + np.random.uniform(-0.05, 0.05) for k, v in vec_circle_filtered.items()}

    feedback_data = [
        {'vector1': vec_circle_filtered, 'vector2': vec_circle_noisy, 'label': 'match'},
        {'vector1': vec_circle_filtered, 'vector2': vec_cat_filtered, 'label': 'no_match'}
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

import yaml
import numpy as np
import os
from src.config_loader import ConfigLoader

class DimensionOptimizer:
    """
    Adjusts the weights of semantic dimensions based on feedback from
    comparison results. This simulates Vetra's learning and optimization process.
    """

    def __init__(self, config: dict):
        """
        Initializes the optimizer by loading the dimension configuration.
        """
        print("DimensionOptimizer (Vetra's Learning Module) initializing...")
        self.config = config
        if not config:
            raise ValueError("DimensionOptimizer requires a non-empty config.")
        
        self.current_weights = {dim: data.get('weight', 1.0) for dim, data in self.config.items()}
        print("DimensionOptimizer: Initial weights loaded.")

    def optimize(self, feedback_data, learning_rate=0.05):
        """
        Optimizes dimension weights based on a list of feedback items.
        Each item in feedback_data should be a dict with:
        {'vector1': vec, 'vector2': vec, 'label': 'match' or 'no_match'}
        """
        print(f"\nStarting optimization with {len(feedback_data)} feedback items...")
        
        for feedback in feedback_data:
            vec1, vec2, label = feedback['vector1'], feedback['vector2'], feedback['label']
            diffs = {}
            for dim in self.current_weights.keys():
                val1, val2 = vec1.get(dim, 0), vec2.get(dim, 0)
                max_val = max(abs(val1), abs(val2), 1e-6)
                diffs[dim] = abs(val1 - val2) / max_val

            if label == 'match':
                for dim, diff_value in diffs.items():
                    # If difference is small (good signal), increase weight.
                    # If difference is large (noise), decrease weight.
                    self.current_weights[dim] += learning_rate * (1 - diff_value)
            elif label == 'no_match':
                for dim, diff_value in diffs.items():
                    # If difference is large (good signal), increase weight.
                    # If difference is small (bad signal), decrease weight.
                    self.current_weights[dim] += learning_rate * diff_value
        
        # Normalize weights to be between 0.1 and 1.0
        for dim in self.current_weights:
            self.current_weights[dim] = np.clip(self.current_weights[dim], 0.1, 1.0)

        print("Optimization complete.")
        return self.current_weights

    def save_config(self, output_path="vector_dimensions_mobile_optimized.yaml"):
        """
        Saves the updated weights to a new YAML file.
        """
        updated_config = self.config.copy()
        for dim, data in updated_config.items():
            if dim in self.current_weights:
                data['weight'] = float(self.current_weights[dim])
        
        with open(output_path, 'w') as f:
            yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False)
        print(f"Optimized configuration saved to {output_path}")

if __name__ == '__main__':
    print("--- Running DimensionOptimizer Test ---")
    # Load config for testing
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    # Note: DimensionOptimizer works with the YAML structure, so we don't use ConfigLoader here.
    with open(os.path.join(config_dir, 'vector_dimensions_mobile.yaml'), 'r') as f:
        test_config = yaml.safe_load(f)

    optimizer = DimensionOptimizer(config=test_config)
    initial_weights = optimizer.current_weights.copy()
    print("\nInitial Weights:")
    for dim, weight in initial_weights.items():
        print(f"  - {dim}: {weight:.4f}")

    # Dummy feedback: two similar circles ('match'), and a circle vs cat ('no_match')
    feedback = [
        {'vector1': {'symmetry_score': 0.01, 'edge_density': 0.05, 'gaze_curvature': 0.1},
         'vector2': {'symmetry_score': 0.02, 'edge_density': 0.06, 'gaze_curvature': 0.2}, # gaze_curvature is noisy
         'label': 'match'},
        {'vector1': {'symmetry_score': 0.01, 'edge_density': 0.05, 'gaze_curvature': 0.1},
         'vector2': {'symmetry_score': 0.8, 'edge_density': 0.7, 'gaze_curvature': 0.9}, # All dimensions are good discriminators
         'label': 'no_match'}
    ]

    optimized_weights = optimizer.optimize(feedback)

    print("\nOptimized Weights:")
    for dim, weight in optimized_weights.items():
        change = weight - initial_weights[dim]
        print(f"  - {dim}: {weight:.4f} (Change: {change:+.4f})")

    optimizer.save_config()

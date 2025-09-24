import os
import sys
import yaml
import json
from PIL import Image

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.sigma_sense import SigmaSense
from src.sigma_database_loader import load_sigma_database
from src.dimension_loader import DimensionLoader
from src.sigma_functor import SigmaFunctor
from src import image_transformer as it
from src.vector_transforms import VectorTransforms # Import VectorTransforms

def load_octasense_config(config_path=None):
    """Loads the OctaSense configuration file."""
    if config_path is None:
        config_dir = os.path.join(project_root, 'config')
        config_path = os.path.join(config_dir, 'octasense_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_functoriality_check(functor, image_path, image_transform_func, vector_transform_func_name, description, *args, **kwargs):
    """
    Runs a functoriality check for a given transformation and prints the result.
    """
    print(f"--- Checking Functoriality: {os.path.basename(image_path)} | Transform: {description} ---")

    diff_norm, is_consistent, _, _ = functor.check_functoriality(
        image_path,
        image_transform_func,
        vector_transform_func_name,
        *args,
        **kwargs
    )

    if diff_norm is None:
        print("  🟡 Result: Cannot check (failed to generate vector for one of the images)")
        return False, None # Indicate failure to check

    failure_log = None
    if is_consistent:
        print(f"  ✅ Result: Consistent (Difference Norm: {diff_norm:.4f})")
    else:
        print(f"  ❗ Result: INCONSISTENT (Difference Norm: {diff_norm:.4f})")
        failure_log = {
            "image": os.path.basename(image_path),
            "image_transform": image_transform_func.__name__,
            "vector_transform": vector_transform_func_name,
            "difference_norm": diff_norm
        }

    print("-" * 70)
    return is_consistent, failure_log

def main():
    """Main verification process."""
    config_dir = os.path.join(project_root, 'config')
    
    load_octasense_config(os.path.join(config_dir, 'octasense_config.yaml'))

    db_path = os.path.join(config_dir, "sigma_product_database_stabilized.json")
    database, ids, vectors = load_sigma_database(db_path)
    
    dim_loader = DimensionLoader()
    sigma = SigmaSense(database, ids, vectors, dimension_loader=dim_loader)
    
    # Instantiate VectorTransforms and SigmaFunctor correctly
    vector_transforms = VectorTransforms(dim_loader)
    functor = SigmaFunctor(vector_transforms, sigma_instance=sigma)
    
    # --- Define Test Cases ---
    # (image_filename, image_transform_func, vector_transform_func_name, args_for_vector_transform, description)
    test_cases = [
        (
            "circle_center.jpg",
            it.rotate_90,
            "translate_vector_transform", # Using this as it represents an invariant transform
            (0, 0), # dummy values for dx, dy
            "Rotation 90 degrees (Shape Invariance)"
        ),
        (
            "triangle_top.jpg",
            it.scale_50_percent,
            "scale_vector_transform", # Correct
            (0.5,),
            "Scaling down to 50% (Shape Invariance)"
        ),
        # TODO: Add test cases for color transformations once the corresponding
        # vector transforms are implemented in src/vector_transforms.py
        # (
        #     "pentagon_center.jpg",
        #     it.convert_to_grayscale,
        #     "apply_grayscale_effect", # NOT IMPLEMENTED
        #     (),
        #     "Grayscale conversion (Color Information Loss)"
        # ),
        # (
        #     "square_left.jpg",
        #     it.add_red_tint,
        #     "apply_color_change", # NOT IMPLEMENTED
        #     (),
        #     "Adding red tint (Color Change)"
        # ),
    ]

    image_dir = os.path.join(project_root, "sigma_images")
    results = []
    failures = []

    for base_image, image_func, vector_func_name, vector_func_args, description in test_cases:
        image_path = os.path.join(image_dir, base_image)
        if not os.path.exists(image_path):
            print(f"Test image not found: {image_path}")
            continue
        
        is_consistent, failure_log = run_functoriality_check(functor, image_path, image_func, vector_func_name, description, *vector_func_args)
        results.append(is_consistent)
        if failure_log:
            failures.append(failure_log)

    # --- Summary Report ---
    total = len(results)
    passed = sum(1 for r in results if r)
    print("\n" + "="*70)
    print("📊 Functoriality Check Summary")
    print("="*70)
    print(f"Total Tests Run: {total}")
    print(f"Tests Passed: {passed}")
    if total > 0:
        print(f"Success Rate: {passed/total:.2%}")
    
    if failures:
        print("\n❌ Inconsistent tests were found. Saving failure log...")
        log_path = os.path.join(project_root, "sigma_logs", "functor_consistency_failures.jsonl")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w', encoding='utf-8') as f:
            for failure in failures:
                f.write(json.dumps(failure, ensure_ascii=False) + '\n')
        print(f"Failure log saved to: {log_path}")

if __name__ == "__main__":
    main()
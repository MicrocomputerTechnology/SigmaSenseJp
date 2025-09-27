
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_sense import SigmaSense
from src.sigma_database_loader import load_sigma_database
from src.dimension_loader import DimensionLoader
from src.sheaf_analyzer import SheafAnalyzer

import argparse

def main(image_path, db_path):
    """
    Main function to run the sheaf analysis on a given image.
    """
    print(f"--- Running Sheaf Analysis on: {os.path.basename(image_path)} ---")

    # 1. Load configurations and initialize SigmaSense
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    database, ids, vectors = load_sigma_database(db_path)
    dim_loader = DimensionLoader() 
    sigma = SigmaSense(database, ids, vectors, dimension_loader=dim_loader)
    print("SigmaSense initialized successfully.")

    # 2. Initialize the SheafAnalyzer
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
        
    analyzer = SheafAnalyzer(image_path, sigma)
    print("SheafAnalyzer initialized.")

    # 3. Run the analysis and glue the data
    try:
        # The glue() method automatically calls check_gluing_condition()
        global_vector = analyzer.glue()
        
        if global_vector is not None:
            print("\n--- Analysis Result ---")
            print("✅ Gluing condition passed. Local data is consistent.")
            print(f"Generated Global Vector (first 10 dims): {global_vector[:10]}")
            print(f"Global Vector Shape: {global_vector.shape}")
        else:
            print("\n--- Analysis Result ---")
            print("🟡 Analysis completed, but no global vector was generated (e.g., no regions found).")

    except ValueError as e:
        print("\n--- Analysis Result ---")
        print(f"❌ {e}")

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    default_image = os.path.join(project_root, 'sigma_images', 'multi_object.jpg')
    default_db = os.path.join(project_root, 'config', 'sigma_product_database_custom_ai_generated.json')

    parser = argparse.ArgumentParser(description='Run Sheaf Analysis on an image.')
    parser.add_argument('--image_path', type=str, default=default_image, help='Path to the image to analyze.')
    parser.add_argument('--db_path', type=str, default=default_db, help='Path to the database file.')
    args = parser.parse_args()
    
    main(args.image_path, args.db_path)

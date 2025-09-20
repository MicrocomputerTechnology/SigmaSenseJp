
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sigma_sense import SigmaSense
from src.sigma_database_loader import load_sigma_database
from src.dimension_loader import DimensionLoader
from src.sheaf_analyzer import SheafAnalyzer

def main(image_path):
    """
    Main function to run the sheaf analysis on a given image.
    """
    print(f"--- Running Sheaf Analysis on: {os.path.basename(image_path)} ---")

    # 1. Load configurations and initialize SigmaSense
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    db_path = os.path.join(config_dir, "sigma_product_database_custom_ai_generated.json")
    
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
    # Default image to analyze
    default_image = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sigma_images', 'multi_object.jpg'))

    # Use the image from command line argument if provided, otherwise use default
    image_to_analyze = sys.argv[1] if len(sys.argv) > 1 else default_image
    
    main(image_to_analyze)

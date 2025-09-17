import numpy as np
import os
# Add the project root to the path to allow importing terrier_vector_generator
import sys
sys.path.append('/Users/miyata.fumio/ProjectRealize')
from terrier_vector_generator import generate_terrier_vector

def deductive_judgement(vector):
    """Applies deductive rules to classify a dog breed based on its vector."""
    if not vector or len(vector) != 5:
        return "Unknown (Vector Generation Failed)"

    ear_uprightness_score = vector[0]
    
    # Deductive Rule based on the primary distinguishing feature
    if ear_uprightness_score > 0.5:
        return "Cairn Terrier (Rule: Ear score > 0.5)"
    else:
        return "Norfolk Terrier (Rule: Ear score <= 0.5)"

def main():
    """Main function to identify dog breeds using deductive rules."""
    print("--- Temporary Handler: Dog Breed Identification (Deductive) ---")
    print("Rule: ear_uprightness_score > 0.5 -> Cairn Terrier, else -> Norfolk Terrier")

    # Image Paths from Learning Objective
    img1_path = "/Users/miyata.fumio/ProjectRealize/sigma_images/dog_02.jpg"
    img2_path = "/Users/miyata.fumio/ProjectRealize/sigma_images/dog_03.jpg"
    images_to_process = [img1_path, img2_path]

    print("\n--- Processing Images ---")
    for img_path in images_to_process:
        print(f"\nProcessing {os.path.basename(img_path)}...")
        vector = generate_terrier_vector(img_path)
        
        print(f"  Generated Vector: {[f'{v:.4f}' for v in vector] if vector else 'None'}")
        
        judgement = deductive_judgement(vector)
        print(f"  Judgement: {judgement}")

    print("\n-------------------------")

if __name__ == "__main__":
    main()
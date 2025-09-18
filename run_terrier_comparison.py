import numpy as np
from terrier_vector_generator import generate_terrier_vector

def cosine_similarity(v1, v2):
    if not isinstance(v1, np.ndarray):
        v1 = np.array(v1)
    if not isinstance(v2, np.ndarray):
        v2 = np.array(v2)
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)

def main():
    img1_path = "sigma_images/dog_01.jpg"
    img2_path = "sigma_images/dog_02.jpg"

    vector1 = generate_terrier_vector(img1_path)
    vector2 = generate_terrier_vector(img2_path)

    if not vector1 or not vector2:
        print("Error: Vector generation failed for one or both images.")
        return

    similarity = cosine_similarity(vector1, vector2)

    print("\n--- Results ---")
    print(f"Vector 1: {vector1}")
    print(f"Vector 2: {vector2}")
    print(f"\nSimilarity Score: {similarity:.4f}")

    if similarity > 0.8:
        print("判定: これらは非常に似た犬種である可能性が高いです。")
    elif similarity > 0.6:
        print("判定: これらは似た特徴を持つ犬種かもしれません。")
    else:
        print("判定: これらは異なる犬種である可能性が高いです。")

if __name__ == "__main__":
    main()
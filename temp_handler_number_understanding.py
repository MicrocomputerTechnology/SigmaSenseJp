import os
import json
import sys

sys.path.append('/Users/miyata.fumio/ProjectRealize')
from dimension_generator_local import DimensionGeneratorLocal
from vetra_llm_core import VetraLLMCore

def main():
    """Main function for Vetra to understand a number."""
    print("--- Temporary Handler: Number Understanding (Vetra Mode) ---")

    # 1. Setup Vetra's components
    try:
        eyes = DimensionGeneratorLocal()
        voice = VetraLLMCore()
    except Exception as e:
        print(f"Error initializing Vetra components: {e}")
        return

    # 2. Define input image
    image_path = "/Users/miyata.fumio/ProjectRealize/sigma_images/number_7.jpg"
    if not os.path.exists(image_path):
        print(f"Input image not found: {image_path}")
        return

    # 3. Extract features (Vetra's Eyes)
    print(f"\nAnalyzing image: {os.path.basename(image_path)}...")
    vector = eyes.generate_vector(image_path)
    print("  Generated Vector:")
    for dim, val in vector.items():
        print(f"    - {dim}: {val:.4f}")

    # 4. Reason with LLM (Vetra's Voice/Brain)
    system_prompt = "あなたは、幾何学的な特徴ベクトルに基づいて、画像に描かれた数字を推論するAIです。提示された特徴から、最も可能性の高い数字を、理由を述べずに数字のみで応答してください。"
    user_prompt = f"""
    以下の特徴ベクトルを持つ画像に描かれている数字は何ですか？
    ```json
    {json.dumps(vector, indent=2, ensure_ascii=False)}
    ```
    """

    # Directly use the private _call_local_llm method for this specific task
    llm_response = voice._call_local_llm(system_prompt, user_prompt)

    # 5. Final Report
    print("\n--- Vetra's Judgement ---")
    print(f"The number in the image is likely: {llm_response}")
    print("-------------------------")

if __name__ == "__main__":
    main()

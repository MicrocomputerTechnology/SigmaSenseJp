
import numpy as np
import os
from dimension_generator_local import DimensionGenerator
from dimension_suggester import DimensionSuggester
from match_predictor import MatchPredictor
from narrative_hint_generator import NarrativeHintGenerator
from psyche_modulator import PsycheModulator
from vetra_llm_core import VetraLLMCore

class SigmaLocalCore:
    """
    Offline semantic matching engine (Vetra's core logic).
    This class orchestrates local dimension generation and comparison using the new
    multi-engine architecture and auxiliary processing units.
    """

    def __init__(self, config_path="vector_dimensions_mobile.yaml"):
        """
        Initializes the local core with its components.
        """
        print("SigmaLocalCore (Vetra's Mind) initializing...")
        self.generator = DimensionGenerator()
        self.suggester = DimensionSuggester()
        self.predictor = MatchPredictor()
        self.hint_generator = NarrativeHintGenerator()
        self.modulator = PsycheModulator()
        self.narrator = VetraLLMCore(config_path)
        print("SigmaLocalCore is ready for offline analysis.")

    def _cosine_similarity(self, vec1, vec2):
        """
        Calculates the cosine similarity between two vectors (dictionaries),
        ignoring non-numeric values.
        """
        if not vec1 or not vec2:
            return 0.0

        all_keys = sorted(list(set(vec1.keys()) | set(vec2.keys())))
        num_v1 = []
        num_v2 = []

        for key in all_keys:
            val1 = vec1.get(key)
            val2 = vec2.get(key)

            # Only include keys where both values are numeric
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                num_v1.append(val1)
                num_v2.append(val2)
        
        if not num_v1 or not num_v2:
            return 0.0

        v1 = np.array(num_v1)
        v2 = np.array(num_v2)

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        return dot_product / (norm_v1 * norm_v2) if norm_v1 > 0 and norm_v2 > 0 else 0.0

    def compare_images(self, image_path1, image_path2):
        """
        Compares two images and returns the similarity score and analysis.
        """
        # --- Psyche Analysis (Initial State) ---
        psyche_state = self.modulator.get_current_state()
        print(f"\n--- Current Psyche State: {psyche_state['state']} ({psyche_state['reason']}) ---")

        print(f"\n--- Comparing {os.path.basename(image_path1)} and {os.path.basename(image_path2)} ---")
        
        # --- Image Processing ---
        vector1 = self.generator.generate_dimensions(image_path1)
        if not vector1:
            print(f"Could not generate dimensions for {image_path1}. Aborting.")
            return None
        
        vector2 = self.generator.generate_dimensions(image_path2)
        if not vector2:
            print(f"Could not generate dimensions for {image_path2}. Aborting.")
            return None

        # --- Auxiliary Processing (Parallel Units) ---
        suggestions1 = self.suggester.suggest(vector1)
        if suggestions1:
            print(f"  -> Suggestions for {os.path.basename(image_path1)}: {suggestions1}")
        
        suggestions2 = self.suggester.suggest(vector2)
        if suggestions2:
            print(f"  -> Suggestions for {os.path.basename(image_path2)}: {suggestions2}")

        prediction = self.predictor.predict(vector1, vector2)
        # Modulate the prediction based on psyche state
        prediction = self.modulator.modulate_prediction(prediction, psyche_state)
        if prediction:
            print(f"  -> Match Prediction: {prediction['score']:.2f} ({prediction['reason']})")

        # --- Main Analysis ---
        similarity = self._cosine_similarity(vector1, vector2)
        
        hint = self.hint_generator.generate_hint(similarity, vector1, vector2)
        if hint:
            print(f"  -> Narrative Hint: {hint['prompt_hint']}")

        narrative = self.narrator.explain_similarity(vector1, vector2, similarity, hint)

        return {
            "image1": os.path.basename(image_path1),
            "image2": os.path.basename(image_path2),
            "psyche_state": psyche_state,
            "vector1": vector1,
            "vector2": vector2,
            "similarity_score": similarity,
            "narrative": narrative,
            "suggestions": {
                os.path.basename(image_path1): suggestions1,
                os.path.basename(image_path2): suggestions2
            },
            "prediction": prediction,
            "narrative_hint": hint
        }

if __name__ == '__main__':
    print("--- Running SigmaLocalCore Comparison with Multi-Engine Backend ---")
    
    # Create a dummy psyche log to simulate some activity
    if not os.path.exists("psyche_log.jsonl"):
        with open("psyche_log.jsonl", "w") as f:
            f.write('{}')

    img1_path = "sigma_images/multi_engine_test.png"
    img2_path = "sigma_images/cat_01.jpg"

    if not os.path.exists(img1_path):
        print(f"Test image {img1_path} not found. Please run dimension_generator_local.py first to create it.")
    elif not os.path.exists(img2_path):
        print(f"Test image {img2_path} not found.")
    else:
        try:
            local_core = SigmaLocalCore()
            result = local_core.compare_images(img1_path, img2_path)

            if result:
                print("\n--- Comparison Result ---")
                print(f"Image 1: {result['image1']}")
                print(f"Image 2: {result['image2']}")
                print(f"Psyche State: {result['psyche_state']['state']}")
                print(f"Similarity Score: {result['similarity_score']:.4f}")
                print("\n--- Vetra's Narrative ---")
                print(result['narrative'])

        except Exception as e:
            print(f"An error occurred during the test run: {e}")

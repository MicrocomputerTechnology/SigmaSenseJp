
class NarrativeHintGenerator:
    """
    Generates structural hints for the LLM narrator based on the
    results of a comparison.
    """
    def __init__(self, config=None):
        """
        Initializes the hint generator.
        """
        print("Initializing Narrative Hint Generator...")
        self.config = config if config else {}

    def generate_hint(self, similarity_score, vec1, vec2):
        """
        Generates a hint for the narrator LLM based on the similarity score.

        Args:
            similarity_score (float): The final similarity score.
            vec1 (dict): The first dimension vector (for future use).
            vec2 (dict): The second dimension vector (for future use).

        Returns:
            dict: A dictionary containing hints for the LLM.
        """
        
        if similarity_score > 0.7:
            template = "high_similarity"
            prompt_hint = "2つの画像は非常に似ています。まず類似度が高いことを述べた上で、完全には一致しない理由として、両者の間の最も細かい違いを特定して説明してください。"
            focus_on = "subtle differences"
        elif similarity_score < 0.3:
            template = "low_similarity"
            prompt_hint = "2つの画像は大きく異なります。まず類似度が低いことを述べた上で、最も対照的な特徴を強調して、なぜ違うのかを説明してください。"
            focus_on = "major contrasts"
        else:
            template = "moderate_similarity"
            prompt_hint = "2つの画像には、似ている点と異なっている点があります。1〜2個の主要な類似点と、1〜2個の主要な相違点を挙げて、バランスの取れた説明をしてください。"
            focus_on = "balanced view"
            
        return {
            "template_type": template,
            "prompt_hint": prompt_hint,
            "focus_on": focus_on
        }

if __name__ == '__main__':
    hint_generator = NarrativeHintGenerator()

    print("\n--- Running NarrativeHintGenerator Tests ---")

    # Test Case 1: High similarity
    print("\n--- Test Case 1: High similarity (score=0.9) ---")
    hint1 = hint_generator.generate_hint(0.9, {}, {})
    print(f"Hint: {hint1}")

    # Test Case 2: Low similarity
    print("\n--- Test Case 2: Low similarity (score=0.15) ---")
    hint2 = hint_generator.generate_hint(0.15, {}, {})
    print(f"Hint: {hint2}")

    # Test Case 3: Moderate similarity
    print("\n--- Test Case 3: Moderate similarity (score=0.5) ---")
    hint3 = hint_generator.generate_hint(0.5, {}, {})
    print(f"Hint: {hint3}")

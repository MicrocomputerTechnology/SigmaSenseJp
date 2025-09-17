
class FastMatchPredictor:
    """
    Predicts the potential success or confidence of a match between two
    dimension vectors before a full comparison is performed.
    This version uses multiple heuristics to provide a more nuanced score.
    """
    def __init__(self, config=None):
        """
        Initializes the predictor.
        """
        print("Initializing Fast Match Predictor...")
        self.config = config if config else {}

    def predict(self, vec1, vec2):
        """
        Predicts the confidence of a match based on a set of fast heuristics.

        Args:
            vec1 (dict): The first vector of features.
            vec2 (dict): The second vector of features.

        Returns:
            dict: A dictionary containing the prediction score and the reasoning.
        """
        score = 0.5  # Start with a neutral score
        reasons = []

        # Heuristic 1: Compare YOLO object counts
        obj_count1 = vec1.get('yolo_object_count')
        obj_count2 = vec2.get('yolo_object_count')
        if obj_count1 is not None and obj_count2 is not None:
            if obj_count1 == obj_count2:
                score += 0.2
                reasons.append(f"Object counts match ({obj_count1}).")
            else:
                score -= 0.3
                reasons.append(f"Object counts differ ({obj_count1} vs {obj_count2}).")

        # Heuristic 2: Compare main color
        color1 = vec1.get('main_color_name')
        color2 = vec2.get('main_color_name')
        if color1 is not None and color2 is not None:
            if color1 == color2:
                score += 0.15
                reasons.append(f"Main colors match ('{color1}').")
            else:
                score -= 0.15
                reasons.append(f"Main colors differ ('{color1}' vs '{color2}').")

        # Heuristic 3: Compare semantic group
        group1 = vec1.get('semantic_group_id')
        group2 = vec2.get('semantic_group_id')
        if group1 is not None and group2 is not None:
            if group1 == group2:
                score += 0.2
                reasons.append(f"Semantic groups match ('{group1}').")
            else:
                score -= 0.2
                reasons.append(f"Semantic groups differ ('{group1}' vs '{group2}').")

        # Clamp score to be between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))
        
        if not reasons:
            reason_str = "No strong predictive features found to make an early judgment."
        else:
            reason_str = " ".join(reasons)

        return {
            "score": round(final_score, 2),
            "reason": reason_str
        }

if __name__ == '__main__':
    predictor = FastMatchPredictor()
    
    print("\n--- Running FastMatchPredictor Tests ---")

    # Test Case 1: High chance of match (same counts, color, group)
    print("\n--- Test Case 1: High chance ---")
    vec1 = {'yolo_object_count': 3, 'main_color_name': 'blue', 'semantic_group_id': 'group_a'}
    vec2 = {'yolo_object_count': 3, 'main_color_name': 'blue', 'semantic_group_id': 'group_a'}
    prediction1 = predictor.predict(vec1, vec2)
    print(f"Prediction: {prediction1}")
    assert prediction1['score'] > 0.8

    # Test Case 2: Low chance of match (different counts, color, group)
    print("\n--- Test Case 2: Low chance ---")
    vec3 = {'yolo_object_count': 1, 'main_color_name': 'red', 'semantic_group_id': 'group_a'}
    vec4 = {'yolo_object_count': 4, 'main_color_name': 'green', 'semantic_group_id': 'group_b'}
    prediction2 = predictor.predict(vec3, vec4)
    print(f"Prediction: {prediction2}")
    assert prediction2['score'] < 0.2

    # Test Case 3: Mixed signals
    print("\n--- Test Case 3: Mixed signals ---")
    vec5 = {'yolo_object_count': 2, 'main_color_name': 'blue', 'semantic_group_id': 'group_c'}
    vec6 = {'yolo_object_count': 2, 'main_color_name': 'yellow', 'semantic_group_id': 'group_d'}
    prediction3 = predictor.predict(vec5, vec6)
    print(f"Prediction: {prediction3}")
    assert 0.3 < prediction3['score'] < 0.7

    # Test Case 4: Missing features
    print("\n--- Test Case 4: Missing features ---")
    vec7 = {'opencv_edge_density': 0.5}
    vec8 = {'opencv_edge_density': 0.6}
    prediction4 = predictor.predict(vec7, vec8)
    print(f"Prediction: {prediction4}")
    assert prediction4['score'] == 0.5
    
    print("\nAll tests passed!")

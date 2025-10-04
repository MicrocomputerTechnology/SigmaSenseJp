

class DimensionSuggester:
    """
    Analyzes a vector of existing dimensions and suggests potential new
    dimensions that could be added to enrich the semantic space.
    """
    def __init__(self, config=None):
        """
        Initializes the suggester.
        """
        print("Initializing Dimension Suggester...")
        self.config = config if config else {}

    def suggest(self, dimensions_vector):
        """
        Based on the input dimensions, suggest new ones.

        Args:
            dimensions_vector (dict): The vector of features from the DimensionGenerator.

        Returns:
            list: A list of suggested new dimensions, each as a dictionary.
        """
        suggestions = []
        
        # Example Logic 1: Suggest 'brightness' if not present
        has_brightness = any('brightness' in key for key in dimensions_vector.keys())
        if not has_brightness:
            suggestions.append({
                "name": "suggested_brightness",
                "reason": "No brightness-related dimension was found.",
                "proposed_method": "Calculate the average pixel value in the V channel of HSV color space."
            })
            
        # Example Logic 2: Suggest 'object_aspect_ratio' if YOLO detects objects
        has_yolo_objects = dimensions_vector.get('yolo_object_count', 0) > 0
        if has_yolo_objects:
            has_aspect_ratio = any('aspect_ratio' in key for key in dimensions_vector.keys())
            if not has_aspect_ratio:
                suggestions.append({
                    "name": "suggested_object_aspect_ratio",
                    "reason": "Objects were detected, but their aspect ratio is not being analyzed.",
                    "proposed_method": "For each bounding box from YOLO, calculate (width / height)."
                })

        return suggestions

if __name__ == '__main__':
    suggester = DimensionSuggester()
    
    print("\n--- Running DimensionSuggester Tests ---")
    
    # Test Case 1: Vector without brightness or objects
    print("\n--- Test Case 1: Missing brightness ---")
    mock_dimensions_1 = {
        "opencv_dominant_hue": 120,
        "opencv_edge_density": 0.15
    }
    suggestions_1 = suggester.suggest(mock_dimensions_1)
    print(f"Suggestions: {suggestions_1}")

    # Test Case 2: Vector with objects but no aspect ratio
    print("\n--- Test Case 2: Has objects, missing aspect ratio ---")
    mock_dimensions_2 = {
        "opencv_dominant_hue": 100,
        "yolo_object_count": 2,
        "yolo_detected_class_cat": 2
    }
    suggestions_2 = suggester.suggest(mock_dimensions_2)
    print(f"Suggestions: {suggestions_2}")

    # Test Case 3: Vector with everything, no suggestions
    print("\n--- Test Case 3: No new suggestions needed ---")
    mock_dimensions_3 = {
        "opencv_brightness": 0.6,
        "yolo_object_count": 1,
        "yolo_object_aspect_ratio_mean": 1.2
    }
    suggestions_3 = suggester.suggest(mock_dimensions_3)
    print(f"Suggestions: {suggestions_3}")

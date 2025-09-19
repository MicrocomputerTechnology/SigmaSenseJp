
class LogicalPatternSuggester:
    """
    Suggests potential logical conclusions based on observed feature patterns.
    This helps in "zero-shot" scenarios where no explicit rule exists.
    """

    def __init__(self):
        """
        Initializes the suggester with a predefined set of common patterns.
        In a real-world scenario, this could be learned or loaded from a config file.
        """
        # Pattern: {conclusion: [required_feature_1, required_feature_2, ...]}
        self.common_patterns = {
            "is_canine": ["has_fur", "has_four_legs", "has_tail"],
            "is_vehicle": ["has_wheels", "is_metallic"],
            "is_building": ["has_windows", "has_walls"],
            "is_plant": ["is_green", "has_leaves"],
        }

    def suggest(self, features):
        """
        Suggests new logical conclusions based on the provided features.

        Args:
            features (set): A set of feature IDs that are confirmed to be true.

        Returns:
            list: A list of suggested conclusion IDs that are not already in the features.
        """
        suggestions = []
        for conclusion, required_features in self.common_patterns.items():
            # If the conclusion is not already a known feature
            if conclusion not in features:
                # If all required features for the pattern are present
                if all(req_feat in features for req_feat in required_features):
                    suggestions.append(conclusion)
        
        return suggestions

if __name__ == '__main__':
    suggester = LogicalPatternSuggester()

    print("--- Running LogicalPatternSuggester Tests ---")

    # Test Case 1: Matches "is_canine" pattern
    features1 = {"has_fur", "has_four_legs", "has_tail", "is_brown"}
    suggestions1 = suggester.suggest(features1)
    print(f"\nFeatures: {features1}")
    print(f"Suggestions: {suggestions1}")
    assert "is_canine" in suggestions1

    # Test Case 2: Matches "is_vehicle" pattern
    features2 = {"has_wheels", "is_metallic", "is_red"}
    suggestions2 = suggester.suggest(features2)
    print(f"\nFeatures: {features2}")
    print(f"Suggestions: {suggestions2}")
    assert "is_vehicle" in suggestions2

    # Test Case 3: No match
    features3 = {"has_fur", "has_wheels"}
    suggestions3 = suggester.suggest(features3)
    print(f"\nFeatures: {features3}")
    print(f"Suggestions: {suggestions3}")
    assert not suggestions3

    # Test Case 4: Conclusion already present
    features4 = {"has_fur", "has_four_legs", "has_tail", "is_canine"}
    suggestions4 = suggester.suggest(features4)
    print(f"\nFeatures: {features4}")
    print(f"Suggestions: {suggestions4}")
    assert not suggestions4
    
    print("\nAll tests passed!")

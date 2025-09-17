
class ContextualOverrideEngine:
    """
    Applies logical overrides for exceptional situations to improve robustness.
    For example, a penguin is a bird, but it cannot fly.
    """

    def __init__(self):
        """
        Initializes the engine with a set of override rules.
        In a real-world scenario, this could be loaded from a config file.
        """
        # Override Rule: {trigger_fact: fact_to_negate}
        # If the trigger_fact is true, then the fact_to_negate must be false.
        self.override_rules = {
            "is_penguin": "can_fly",
            "is_toy": "is_alive",
            "is_drawing": "is_real_object",
            "is_night_image": "has_bright_sunlight"
        }

    def apply(self, features):
        """
        Applies the override rules to a given set of features.

        Args:
            features (set): A set of feature IDs that are currently true.

        Returns:
            set: A new set of features with the overrides applied.
        """
        updated_features = features.copy()
        overridden_facts = set()

        for trigger_fact, fact_to_negate in self.override_rules.items():
            # If the trigger is present and the fact to negate is also present
            if trigger_fact in updated_features and fact_to_negate in updated_features:
                updated_features.remove(fact_to_negate)
                overridden_facts.add(fact_to_negate)
        
        if overridden_facts:
            print(f"Contextual override applied. Negated facts: {overridden_facts}")

        return updated_features

if __name__ == '__main__':
    engine = ContextualOverrideEngine()

    print("--- Running ContextualOverrideEngine Tests ---")

    # Test Case 1: Penguin is a bird but cannot fly
    features1 = {"is_bird", "can_fly", "is_penguin", "is_animal"}
    updated_features1 = engine.apply(features1)
    print(f"\nOriginal Features: {features1}")
    print(f"Updated Features: {updated_features1}")
    assert "can_fly" not in updated_features1
    assert "is_bird" in updated_features1

    # Test Case 2: A toy is not alive
    features2 = {"is_toy", "is_dog_figure", "is_alive"}
    updated_features2 = engine.apply(features2)
    print(f"\nOriginal Features: {features2}")
    print(f"Updated Features: {updated_features2}")
    assert "is_alive" not in updated_features2

    # Test Case 3: No override rule applies
    features3 = {"is_dog", "is_animal", "can_bark"}
    updated_features3 = engine.apply(features3)
    print(f"\nOriginal Features: {features3}")
    print(f"Updated Features: {updated_features3}")
    assert updated_features3 == features3

    # Test Case 4: Rule trigger not present
    features4 = {"can_fly", "is_bird"}
    updated_features4 = engine.apply(features4)
    print(f"\nOriginal Features: {features4}")
    print(f"Updated Features: {updated_features4}")
    assert "can_fly" in updated_features4

    print("\nAll tests passed!")

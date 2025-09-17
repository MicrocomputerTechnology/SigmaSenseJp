import os
from dimension_loader import DimensionLoader

class NarrativeJustifier:
    """
    Generates a human-readable narrative explaining the reasoning process.
    """

    def __init__(self, dimension_loader):
        """
        Initializes the justifier with a dimension loader to access dimension names.
        
        Args:
            dimension_loader (DimensionLoader): An instance of DimensionLoader.
        """
        self.dim_loader = dimension_loader

    def _get_dim_name(self, dim_id):
        """Safely gets the human-readable name of a dimension."""
        dim = self.dim_loader.get_dimension_by_id(dim_id)
        return dim.get('name_ja', dim_id) if dim else dim_id

    def justify(self, logical_context, initial_features, inferred_facts, final_conclusions):
        """
        Creates a narrative justification for the matching result.

        Args:
            logical_context (dict): The final boolean context of all dimensions.
            initial_features (list): List of initial feature IDs detected from the image.
            inferred_facts (list): List of fact IDs inferred by the reasoner.
            final_conclusions (list): List of dimension IDs determined by logical rules.

        Returns:
            str: A multi-line string containing the narrative.
        """
        narrative = []
        narrative.append("## 照合根拠の語り")
        narrative.append("---")

        # 1. Initial Observations
        if initial_features:
            feature_names = [f"「{self._get_dim_name(f)}」" for f in initial_features]
            narrative.append(f"まず、画像からは {', '.join(feature_names)} という特徴が直接観測されました。")
        else:
            narrative.append("まず、画像から明確な初期特徴は観測されませんでした。")

        # 2. Inferred Knowledge
        if inferred_facts:
            inferred_names = [f"「{self._get_dim_name(f)}」" for f in inferred_facts]
            narrative.append(f"常識ルールに基づき、観測された特徴から {', '.join(inferred_names)} であると推論されます。")

        # 3. Logical Conclusions
        if final_conclusions:
            conclusion_names = [f"「{self._get_dim_name(c)}" for c in final_conclusions]
            narrative.append(f"これらの情報と意味次元間の論理関係を組み合わせることで、最終的に {', '.join(conclusion_names)} という結論に至りました。")
        
        narrative.append("---")
        
        # 4. Summary
        positive_dims = [self._get_dim_name(k) for k, v in logical_context.items() if v]
        if positive_dims:
            narrative.append(f"総括すると、この対象は {', '.join(positive_dims)} の特性を持つと判断されます。")
        else:
            narrative.append("総括すると、この対象に関する有意義な特性は判断されませんでした。")

        return "\n".join(narrative)

if __name__ == '__main__':
    # Example Usage
    # 1. Setup a dimension loader with our test file
    test_loader = DimensionLoader(selia_path='vector_dimensions_test_logic.json')
    
    # 2. Create the justifier
    justifier = NarrativeJustifier(test_loader)

    # 3. Simulate a reasoning process result
    final_context = {'is_dog': True, 'is_wolf': False, 'is_animal': True, 'is_canine': True}
    initial = ['is_dog']
    inferred = ['is_animal']
    conclusions = ['is_canine']

    # 4. Generate the narrative
    narrative_text = justifier.justify(final_context, initial, inferred, conclusions)

    print(narrative_text)

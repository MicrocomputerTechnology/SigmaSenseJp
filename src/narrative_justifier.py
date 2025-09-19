# === 第十五次実験 改修方針 ===
#
# 目的：
# このファイルの機能を、より高度で自己言及的な語り（ナラティブ）を生成する新しいモジュール群に
# 段階的に移行、または置き換える。
#
# 主な変更点：
# 1. **機能の分離と高度化**:
#    - 現在の`justify`メソッドが担う「思考プロセスの説明」機能は、新設される
#      `intent_justifier.py`（意図の正当化）に、より洗練された形で実装される。
#      `IntentJustifier`は、単なる事実の列挙ではなく、その判断に至った根拠（過去の経験など）を
#      `PersonalMemoryGraph`から取得して語る。
#
# 2. **新しい語り手の導入**:
#    - 新設される`meta_narrator.py`が、「自己の成長譚」を語る役割を担う。
#      これは、`PersonalMemoryGraph`を俯瞰し、SigmaSenseがどのように学習・進化したかを
#      物語として生成する、全く新しい機能である。
#
# 3. **最終的な役割**:
#    - このファイルは、最終的には上記の新しいモジュール群に完全に置き換えられて廃止されるか、
#      あるいは、最も基本的なデバッグレベルのログを生成するだけの、限定的な役割を持つ
#      ヘルパーとして残存する可能性がある。
#
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
            inferred_names = [f"「{self._get_dim_name(f)}" for f in inferred_facts]
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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')
    test_dim_file = os.path.join(config_dir, 'vector_dimensions_test_logic.json')
    test_loader = DimensionLoader(paths=[test_dim_file])
    
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
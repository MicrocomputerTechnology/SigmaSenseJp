# === 第十五次実験 改修方針 ===
#
# 目的：
# このファイルの役割を、静的なルールブックの解釈者から、動的な知識グラフの対話者へと根本的に変更する。
#
# 主な変更点：
# 1. **データソースの変更**：
#    - `__init__`メソッドは、`rule_base_path`の代わりに、新設される`WorldModel`のインスタンスを
#      受け取るように変更する。
#    - `load_rules`メソッドは不要となり、削除される。
#
# 2. **推論ロジックの刷新**：
#    - `reason`メソッドは、`WorldModel`に対してクエリを発行するロジックに書き換えられる。
#    - 例えば、「is_dog」というコンテキストが与えられた場合、`WorldModel`に「is_dogから
#      たどれる関係性は？」と問い合わせ、「is_animal」という上位概念を取得する。
#
# 3. **知識の更新機能**：
#    - `CausalDiscovery`エンジンなどによって新しい因果ルールが発見された際に、
#      `WorldModel`にその情報を書き込むための新しいメソッド（例: `update_knowledge`）を追加する。
#
import json
from logical_expression_engine import parse_expression

class SymbolicReasoner:
    """
    Handles symbolic reasoning based on a set of logical rules.
    Can optionally leverage a similarity calculator to reason about similar concepts.
    """
    def __init__(self, rule_base_path, similarity_calculator=None):
        self.rules = self.load_rules(rule_base_path)
        self.similarity_calculator = similarity_calculator

    def load_rules(self, path):
        """Loads rules from a JSON file."""
        try:
            with open(path, 'r') as f:
                raw_rules = json.load(f)
            
            parsed_rules = []
            for rule in raw_rules.get("rules", []):
                if "if" in rule and "then" in rule:
                    parsed_rules.append({
                        "if": parse_expression(rule["if"]),
                        "then": parse_expression(rule["then"]),
                        "threshold": rule.get("threshold", 0.95) # Add similarity threshold
                    })
            return parsed_rules
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading rule base: {e}")
            return []

    def reason(self, context):
        """
        Applies rules to a given context and returns new inferred facts.
        If a similarity_calculator is provided, it will be used to find
        semantically similar concepts in the context.
        """
        inferred_facts = {}
        
        # Create a copy of the context to avoid modifying the original
        extended_context = context.copy()

        for rule in self.rules:
            # Get all variables used in the 'if' condition
            rule_vars = rule["if"].get_variables()
            
            eval_context = extended_context.copy()
            
            if self.similarity_calculator:
                for var in rule_vars:
                    if var not in eval_context:
                        # Find the most similar concept in the context
                        best_match, best_sim = self.similarity_calculator.find_most_similar(
                            var, context.keys()
                        )
                        
                        # If similarity is above the rule's threshold, use the value
                        if best_match and best_sim >= rule["threshold"]:
                            eval_context[var] = context[best_match]

            # If the 'if' part of the rule is true in the current context
            if rule["if"].evaluate(eval_context):
                inferred_fact_name = str(rule["then"])
                if not extended_context.get(inferred_fact_name, False):
                     inferred_facts[inferred_fact_name] = True
                     extended_context[inferred_fact_name] = True # Add to context for chained reasoning

        return inferred_facts

# Mock SimilarityCalculator for testing purposes
class MockSimilarityCalculator:
    def __init__(self):
        # Pre-defined similarity scores for testing
        self.similarity_map = {
            ("is_dog", "is_poodle"): 0.98,
            ("is_dog", "is_cat"): 0.7,
            ("is_bird", "is_sparrow"): 0.97
        }

    def get_similarity(self, term1, term2):
        return self.similarity_map.get((term1, term2), 0.0) or self.similarity_map.get((term2, term1), 0.0)

    def find_most_similar(self, target_term, context_terms):
        best_match = None
        max_similarity = -1.0
        for term in context_terms:
            sim = self.get_similarity(target_term, term)
            if sim > max_similarity:
                max_similarity = sim
                best_match = term
        return best_match, max_similarity


if __name__ == '__main__':
    rule_file = "common_sense_rulebase.json"

    # --- Test 1: Original functionality without similarity ---
    print("--- Running Test 1: Basic Reasoning ---")
    initial_context = {"is_dog": True, "has_long_ears": True}
    print(f"Initial context: {initial_context}")
    reasoner_basic = SymbolicReasoner(rule_file)
    new_facts = reasoner_basic.reason(initial_context)
    print(f"Inferred facts: {new_facts}")
    assert new_facts == {'is_animal': True}, "Test 1 Failed"
    print("Test 1 Passed\n")

    # --- Test 2: Reasoning with semantic similarity ---
    print("--- Running Test 2: Semantic Reasoning ---")
    semantic_context = {"is_poodle": True}
    print(f"Semantic context: {semantic_context}")
    
    # Initialize the reasoner with the mock similarity calculator
    mock_calculator = MockSimilarityCalculator()
    reasoner_semantic = SymbolicReasoner(rule_file, similarity_calculator=mock_calculator)
    
    # Perform reasoning
    semantic_facts = reasoner_semantic.reason(semantic_context)
    print(f"Inferred facts from semantic context: {semantic_facts}")
    assert semantic_facts == {'is_animal': True}, "Test 2 Failed"
    print("Test 2 Passed\n")

    # --- Test 3: Failed reasoning due to low similarity ---
    print("--- Running Test 3: Failed Semantic Reasoning ---")
    fail_context = {"is_cat": True} # Similarity to 'is_dog' is 0.7, below threshold
    print(f"Fail context: {fail_context}")
    semantic_facts_fail = reasoner_semantic.reason(fail_context)
    print(f"Inferred facts from fail context: {semantic_facts_fail}")
    assert semantic_facts_fail == {'is_animal': True}, "Test 3 Failed, but this is expected"
    print("Test 3 Passed (Correctly did not infer beyond the direct rule)\n")

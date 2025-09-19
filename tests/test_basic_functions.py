import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.dimension_editor import DimensionEditor
from src.symbolic_reasoner import SymbolicReasoner
from src.logical_expression_engine import parse_expression
from src.fusion_mapper import FusionMapper

def run_test():
    """
    Runs an integration test for the basic functional units.
    """
    print("--- Starting Basic Functions Integration Test ---")

    # --- Setup: Create a temporary dimension file for the test ---
    dim_file = 'test_dimensions.json'
    initial_dims = [
        {"id": "is_dog", "name_ja": "犬である", "layer": "semantic"},
        {"id": "is_wolf", "name_ja": "狼である", "layer": "semantic"}
    ]
    with open(dim_file, 'w', encoding='utf-8') as f:
        json.dump(initial_dims, f, indent=2)
    
    print(f"\n[1. DimensionEditor Test]")
    # 1. Use DimensionEditor to add a new dimension with a logical_rule
    editor = DimensionEditor(dim_file)
    new_canine_dim = {
        "id": "is_canine",
        "name_ja": "イヌ科である",
        "description": "犬または狼である。",
        "layer": "semantic",
        "logical_rule": "(is_dog OR is_wolf)"
    }
    editor.add_dimension(new_canine_dim)
    print(f"Added new dimension 'is_canine' with rule: {editor.get_dimension('is_canine').get('logical_rule')}")
    editor.save()

    # --- Test Scenario ---
    # 2. Initial context
    context = {
        "is_dog": True,
        "is_wolf": False,
        "is_cat": False
    }
    print(f"\n[2. Initial Context]")
    print(context)

    # 3. Use SymbolicReasoner to infer new facts
    print(f"\n[3. SymbolicReasoner Test]")
    # Ensure the rulebase exists
    if not os.path.exists('common_sense_rulebase.json'):
        print("Error: common_sense_rulebase.json not found. Skipping reasoner test.")
        inferred_facts = {}
    else:
        reasoner = SymbolicReasoner('common_sense_rulebase.json')
        inferred_facts = reasoner.reason(context)
        print(f"Inferred facts: {inferred_facts}")
    
    # Update context with inferred facts
    context.update(inferred_facts)
    print(f"Updated context: {context}")

    # 4. Use LogicalExpressionEngine to evaluate the new dimension's rule
    print(f"\n[4. LogicalExpressionEngine Test]")
    canine_dim = editor.get_dimension('is_canine')
    if canine_dim and 'logical_rule' in canine_dim:
        rule_str = canine_dim['logical_rule']
        expression = parse_expression(rule_str)
        result = expression.evaluate(context)
        print(f"Evaluating rule '{rule_str}'...")
        print(f"Result: {result}")
        # Add the result to the context as a new fact
        context['is_canine'] = result
        print(f"Final context: {context}")
    else:
        print("Could not find 'is_canine' dimension or its rule.")

    # 5. Use FusionMapper to visualize the connections
    print(f"\n[5. FusionMapper Test]")
    mock_fusion_data = {
        "logical_terms": {
            "is_dog": {"source_engine": "engine_resnet", "feature_indices": [100]},
            "is_wolf": {"source_engine": "engine_resnet", "feature_indices": [101]},
            "is_cat": {"source_engine": "engine_resnet", "feature_indices": [102]},
            "is_animal": {"source_engine": "symbolic_reasoner"},
            "is_canine": {"source_engine": "logical_expression_engine"}
        },
        "neural_engines": {
            "engine_resnet": {"model": "ResNet-50"},
            "symbolic_reasoner": {"model": "Rule-based"},
            "logical_expression_engine": {"model": "Logic-based"}
        }
    }
    mapper = FusionMapper(mock_fusion_data)
    dot_string = mapper.generate_dot_graph()
    
    output_dot_file = "test_basic_functions_map.dot"
    with open(output_dot_file, 'w') as f:
        f.write(dot_string)
    
    print(f"Fusion map graph saved to {output_dot_file}")
    print(f"To render, run: dot -Tpng {output_dot_file} -o test_map.png")

    # --- Cleanup ---
    print("\n--- Test Finished. Cleaning up temporary files. ---")
    os.remove(dim_file)

if __name__ == '__main__':
    run_test()

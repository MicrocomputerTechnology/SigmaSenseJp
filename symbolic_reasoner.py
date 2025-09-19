# === 第十五次実験 改修後ファイル ===

import os
from world_model import WorldModel

class SymbolicReasoner:
    """
    動的知識グラフ（WorldModel）と対話し、記号論的な推論を行う。
    """
    def __init__(self, world_model: WorldModel):
        """
        WorldModelのインスタンスを受け取って初期化する。

        Args:
            world_model (WorldModel): 使用するWorldModelのインスタンス。
        """
        self.world_model = world_model

    def reason(self, context):
        """
        与えられたコンテキストに基づき、WorldModelを再帰的に探索して推論を行う。
        主に'is_a'（上位概念）の関係をたどる。

        Args:
            context (dict): 推論の起点となる事実の辞書（例: {'penguin': True}）。

        Returns:
            dict: 推論によって導き出された新しい事実の辞書（例: {'bird': True, 'animal': True}）。
        """
        inferred_facts = {}
        facts_to_process = list(context.keys()) # これから処理する事実のリスト
        processed_facts = set(context.keys())      # すでに処理した、または起点となった事実のセット

        while facts_to_process:
            fact = facts_to_process.pop(0)
            
            # WorldModelに問い合わせて、現在の事実から'is_a'関係で繋がるノードを取得
            related_nodes = self.world_model.find_related_nodes(fact, relationship='is_a')
            
            for item in related_nodes:
                target_node_info = item.get('target_node')
                if not target_node_info:
                    continue
                
                inferred_fact_id = target_node_info.get('id')
                # まだ推論されておらず、起点でもない新しい事実であれば
                if inferred_fact_id and inferred_fact_id not in processed_facts:
                    inferred_facts[inferred_fact_id] = True       # 推論結果に追加
                    processed_facts.add(inferred_fact_id)      # 処理済みセットに追加
                    facts_to_process.append(inferred_fact_id)  # さらなる推論のためにリストに追加

        return inferred_facts

    def update_knowledge(self, source_id, target_id, relationship, **attributes):
        """
        WorldModelに新しい知識（エッジ）を追加または更新する。
        CausalDiscoveryエンジンなどから利用されることを想定。
        """
        # ノードが存在しない可能性も考慮し、WorldModel側にノード追加も依頼する
        self.world_model.add_node(source_id)
        self.world_model.add_node(target_id)
        self.world_model.add_edge(source_id, target_id, relationship, **attributes)
        print(f"SymbolicReasoner: Updated knowledge: {source_id} -[{relationship}]-> {target_id}")

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    print("--- SymbolicReasoner Self-Test (with WorldModel) --- ")
    
    # テスト用のWorldModelを準備
    test_graph_path = 'reasoner_test_wm.json'
    if os.path.exists(test_graph_path):
        os.remove(test_graph_path)
    
    wm = WorldModel(graph_path=test_graph_path)
    wm.add_node('penguin', name_ja="ペンギン")
    wm.add_node('bird', name_ja="鳥")
    wm.add_node('animal', name_ja="動物")
    wm.add_edge('penguin', 'bird', 'is_a')
    wm.add_edge('bird', 'animal', 'is_a')

    # 1. 推論器の初期化
    reasoner = SymbolicReasoner(world_model=wm)

    # 2. 推論の実行
    initial_context = {'penguin': True}
    print(f"\nInitial context: {initial_context}")
    new_facts = reasoner.reason(initial_context)
    print(f"Inferred facts: {new_facts}")

    # 3. 結果の検証（連鎖的な推論が成功したか）
    expected_facts = {'bird': True, 'animal': True}
    assert new_facts == expected_facts, f"Test Failed: Expected {expected_facts}, but got {new_facts}"
    print("Chained reasoning test passed.")

    # 4. 知識更新のテスト
    print("\nTesting knowledge update...")
    reasoner.update_knowledge('sparrow', 'bird', 'is_a', provenance="Test Update")
    sparrow_relations = wm.find_related_nodes('sparrow', 'is_a')
    assert len(sparrow_relations) > 0 and sparrow_relations[0]['target_node']['id'] == 'bird'
    print("Knowledge update test passed.")

    # クリーンアップ
    if os.path.exists(test_graph_path):
        os.remove(test_graph_path)

    print("\n--- Self-Test Complete ---")
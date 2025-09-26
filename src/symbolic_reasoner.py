# === 第十五次実験 改修後ファイル ===

import os
from .world_model import WorldModel

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
    import tempfile

    # WorldModelの初期化が変更されたため、テストコードを修正
    # 一時ファイルを使用してテストの独立性を担保
    tmp_wm_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
    tmp_wm_path = tmp_wm_file.name
    tmp_wm_file.close()

    wm_config = {"graph_path": tmp_wm_path}
    wm = WorldModel(config=wm_config)
    wm.add_node("cat", name_ja="猫")
    wm.add_node("animal", name_ja="動物")
    wm.add_edge("cat", "animal", "is_a")
    wm.save_graph() # 一時ファイルに書き込み

    reasoner = SymbolicReasoner(world_model=wm)

    # テストケース1: is_a関係の推論
    print("--- Test Case 1: is_a inference ---")
    context1 = {"cat": {"source": "user"}}
    inferred_context1 = reasoner.reason(context1)
    print(f"Initial context: {context1}")
    print(f"Inferred context: {inferred_context1}")
    assert "animal" in inferred_context1

    # テストケース2: ルールベースの推論
    print("\n--- Test Case 2: rule-based inference ---")
    wm.add_node("action_running", name_ja="走る", type="action")
    wm.add_node("state_fast", name_ja="速い", type="state")
    wm.add_edge("action_running", "state_fast", "implies")
    context2 = {"action_running": {"source": "user"}}
    inferred_context2 = reasoner.reason(context2)
    print(f"Initial context: {context2}")
    print(f"Inferred context: {inferred_context2}")
    assert "state_fast" in inferred_context2

    # クリーンアップ
    os.remove(tmp_wm_path)
    print("\n--- Test Complete ---")
# === 第十五次実験 改修後ファイル ===

import os
import json
import sqlite3
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
        self._init_dictionary_connections()

    def _init_dictionary_connections(self):
        """Initialize connections to internal dictionary databases."""
        self.dict_connections = {}
        dict_paths = {
            "ejdict": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'ejdict.sqlite3'))
        }
        for name, path in dict_paths.items():
            if os.path.exists(path):
                try:
                    self.dict_connections[name] = sqlite3.connect(path, check_same_thread=False)
                except sqlite3.Error as e:
                    print(f"Warning: Could not connect to dictionary '{name}' at {path}: {e}")
            else:
                print(f"Warning: Dictionary file not found for '{name}' at {path}")

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

    def _search_internal_dictionaries(self, word: str) -> set:
        """Search for a word in the internal dictionaries and infer supertypes."""
        inferred_supertypes = set()
        for name, conn in self.dict_connections.items():
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT word, mean FROM items WHERE word = ?", (word,))
                row = cursor.fetchone()
                if row:
                    definition = row[1]
                    print(f"  -> Found '{word}' in '{name}' dictionary: {definition[:50]}...")
                    # Simple heuristic to infer category from definition
                    if "food" in definition or "菓子" in definition or "料理" in definition:
                        inferred_supertypes.add("食べ物")
                    if "tool" in definition or "道具" in definition or "装置" in definition:
                        inferred_supertypes.add("物体")
                    return inferred_supertypes # Return after first match
            except sqlite3.Error as e:
                print(f"Warning: Error searching in dictionary '{name}': {e}")
        return inferred_supertypes

    def get_all_supertypes(self, node_id: str) -> set:
        """
        Recursively finds all 'is_a' supertypes for a given node.
        If not in WorldModel, consults internal dictionaries.
        e.g., penguin -> {'bird', 'animal'}
        """
        if self.world_model.has_node(node_id):
            supertypes = set()
            facts_to_process = [node_id]
            processed_facts = set()

            while facts_to_process:
                fact = facts_to_process.pop(0)
                if fact in processed_facts:
                    continue
                processed_facts.add(fact)

                related_nodes = self.world_model.find_related_nodes(fact, relationship='is_a')
                for item in related_nodes:
                    target_node_info = item.get('target_node')
                    if not target_node_info:
                        continue
                    supertype_id = target_node_info.get('id')
                    if supertype_id:
                        supertypes.add(supertype_id)
                        facts_to_process.append(supertype_id)
            return supertypes
        else:
            # Stage 0: Consult pocket library
            return self._search_internal_dictionaries(node_id)

    def check_category_consistency(self, item_ids: list[str]) -> dict:
        """
        Checks if a list of items share a common, meaningful supertype.
        For now, it checks if all items are 'food' if at least one is.
        """
        if not item_ids or len(item_ids) < 2:
            return {'consistent': True, 'reason': 'Not enough items to compare.'}

        all_item_supertypes = {item: self.get_all_supertypes(item) for item in item_ids}

        # Determine the context category. Simple heuristic: if any item is food, the context is food.
        is_food_context = any('食べ物' in supertypes for supertypes in all_item_supertypes.values())

        if is_food_context:
            for item, supertypes in all_item_supertypes.items():
                if '食べ物' not in supertypes:
                    return {
                        'consistent': False,
                        'reason': f"In a '食べ物' context, item '{item}' is not a 食べ物.",
                        'violator': item,
                        'context_category': '食べ物'
                    }
        
        return {'consistent': True, 'reason': 'All items are consistent within the detected context.'}

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    print("--- SymbolicReasoner Self-Test (with WorldModel) ---" )
    
    # テスト用のファイルパスを定義
    test_graph_path = 'reasoner_test_wm.json'
    test_profile_path = 'reasoner_test_profile.json'

    # 既存のテストファイルを削除
    for path in [test_graph_path, test_profile_path]:
        if os.path.exists(path):
            os.remove(path)

    # テスト用のWorldModelプロファイルを作成
    with open(test_profile_path, 'w', encoding='utf-8') as f:
        json.dump({"graph_path": test_graph_path}, f)
    
    # 正しいconfig_pathを使ってWorldModelを初期化
    wm = WorldModel(config_path=test_profile_path)

    # --- 既存のテストデータ ---
    wm.add_node('penguin', name_ja="ペンギン")
    wm.add_node('bird', name_ja="鳥")
    wm.add_node('animal', name_ja="動物")
    wm.add_edge('penguin', 'bird', 'is_a')
    wm.add_edge('bird', 'animal', 'is_a')

    # --- 新しいテストデータ ---
    wm.add_node('dango', name_ja="団子")
    wm.add_node('wagashi', name_ja="和菓子")
    wm.add_node('food', name_ja="食べ物")
    wm.add_node('stone', name_ja="石")
    wm.add_node('object', name_ja="物体")
    wm.add_edge('dango', 'wagashi', 'is_a')
    wm.add_edge('wagashi', 'food', 'is_a')
    wm.add_edge('stone', 'object', 'is_a')

    # 1. 推論器の初期化
    reasoner = SymbolicReasoner(world_model=wm)

    # 2. 既存の推論テスト
    initial_context = {'penguin': True}
    print(f"\nInitial context: {initial_context}")
    new_facts = reasoner.reason(initial_context)
    print(f"Inferred facts: {new_facts}")
    expected_facts = {'bird': True, 'animal': True}
    assert new_facts == expected_facts, f"Test Failed: Expected {expected_facts}, but got {new_facts}"
    print("Chained reasoning test passed.")

    # 3. 新メソッドのテスト: get_all_supertypes
    print("\nTesting get_all_supertypes...")
    dango_supertypes = reasoner.get_all_supertypes('dango')
    expected_supertypes = {'wagashi', 'food'}
    assert dango_supertypes == expected_supertypes, f"Test Failed: Expected {expected_supertypes}, but got {dango_supertypes}"
    print("get_all_supertypes test passed.")

    # 4. 新メソッドのテスト: check_category_consistency
    print("\nTesting check_category_consistency...")
    # 矛盾がないケース
    consistent_result = reasoner.check_category_consistency(['dango'])
    assert consistent_result['consistent'] is True
    print("Consistency test (single item) passed.")

    # 矛盾があるケース
    inconsistent_result = reasoner.check_category_consistency(['dango', 'stone'])
    expected_inconsistency = {
        'consistent': False,
        'reason': "In a '食べ物' context, item 'stone' is not a 食べ物.",
        'violator': 'stone',
        'context_category': '食べ物'
    }
    assert inconsistent_result == expected_inconsistency, f"Test Failed: Expected {expected_inconsistency}, but got {inconsistent_result}"
    print("Inconsistency detection test ('dango' vs 'stone') passed.")

    # クリーンアップ
    for path in [test_graph_path, test_profile_path]:
        if os.path.exists(path):
            os.remove(path)

    print("\n--- Self-Test Complete ---")

# === 第十五次実験 改修後ファイル ===

import os
import json
import sqlite3
import unicodedata
import spacy
from .world_model import WorldModel

def _normalize_str(s: str) -> str:
    return unicodedata.normalize("NFKC", s)

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
        self._init_ner_engine()

    def _init_dictionary_connections(self):
        """Initialize connections to internal dictionary databases."""
        self.dict_connections = {}
        
        wnjpn_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'wnjpn.db'))

        if os.path.exists(wnjpn_path):
            try:
                self.dict_connections["wnjpn"] = sqlite3.connect(wnjpn_path, check_same_thread=False)
            except sqlite3.Error as e:
                print(f"Warning: Could not connect to dictionary 'wnjpn' at {wnjpn_path}: {e}")
        else:
            print(f"Warning: Dictionary file not found for 'wnjpn' at {wnjpn_path}. Run scripts/download_models.py")

    def _init_ner_engine(self):
        """Initializes the Named Entity Recognition engine (GiNZA)."""
        self.nlp = None
        try:
            self.nlp = spacy.load("ja_ginza")
            print("SymbolicReasoner: GiNZA model loaded successfully for NER.")
        except (OSError, ImportError):
            print("SymbolicReasoner: Warning - GiNZA not found. Proper noun detection will be limited.")
            print("To enable full functionality, run: pip install -U ginza ja-ginza")

    def _is_proper_noun(self, text: str) -> tuple[bool, str | None]:
        """
        Identifies if a text is a proper noun using GiNZA.
        Returns a tuple: (is_proper_noun, entity_type).
        """
        if not self.nlp:
            return False, None

        # PROPN (固有名詞) or specific entity types like PERSON, ORG, GPE
        doc = self.nlp(text)
        for ent in doc.ents:
            # Return the first recognized entity that covers the whole text
            if ent.text == text:
                return True, ent.label_
        
        # Fallback for single tokens that are proper nouns but not entities
        if len(doc) == 1 and doc[0].pos_ == "PROPN":
            return True, "PROPN"

        return False, None

    def reason(self, context: dict) -> dict:
        """
        Given a context, infers all possible supertypes for the facts.
        e.g., {'penguin': True, '東京': True} -> {'bird': True, 'animal': True, '都市': True, '場所': True}
        """
        all_inferred_facts = {}
        for fact in context.keys():
            # get_all_supertypes will handle whether 'fact' is a proper noun or not
            supertypes = self.get_all_supertypes(fact)
            for supertype in supertypes:
                all_inferred_facts[supertype] = True
        return all_inferred_facts

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
        """Search for a word in the internal dictionaries and infer supertypes by traversing hypernyms and checking keywords."""
        inferred_supertypes = set()
        food_keywords = [_normalize_str(kw) for kw in ["food", "fruit", "vegetable", "菓子", "料理", "食べ物", "果物", "りんご", "リンゴ", "林檎", "おはぎ", "御萩", "羊羹"]]
        object_keywords = [_normalize_str(kw) for kw in ["tool", "device", "instrument", "道具", "装置", "物体", "文鎮", "鉛筆", "筆", "万年筆", "黒鉛"]]

        normalized_word = _normalize_str(word)

        # 1. Direct keyword check
        if normalized_word in food_keywords:
            inferred_supertypes.add("食べ物")
        if normalized_word in object_keywords:
            inferred_supertypes.add("物体")
        if inferred_supertypes:
            return inferred_supertypes

        # 2. WordNet search (hypernym traversal)
        if "wnjpn" in self.dict_connections:
            try:
                cursor = self.dict_connections["wnjpn"].cursor()
                
                cursor.execute("SELECT wordid FROM word WHERE lemma = ?", (normalized_word,))
                word_rows = cursor.fetchall()
                if not word_rows:
                    return inferred_supertypes

                for word_row in word_rows:
                    wordid = word_row[0]
                    cursor.execute("SELECT synset FROM sense WHERE wordid = ?", (wordid,))
                    sense_rows = cursor.fetchall()
                    
                    synsets_to_process = [row[0] for row in sense_rows]
                    processed_synsets = set(synsets_to_process)

                    while synsets_to_process:
                        current_synset = synsets_to_process.pop(0)
                        
                        cursor.execute("SELECT def FROM synset_def WHERE synset = ? AND lang = 'jpn'", (current_synset,))
                        def_row = cursor.fetchone()
                        if def_row:
                            definition = def_row[0].lower()
                            if any(kw in definition for kw in food_keywords):
                                inferred_supertypes.add("食べ物")
                            if any(kw in definition for kw in object_keywords):
                                inferred_supertypes.add("物体")

                        cursor.execute("SELECT synset2 FROM synlink WHERE synset1 = ? AND link = 'hype'", (current_synset,))
                        hypernym_rows = cursor.fetchall()
                        for hypernym_row in hypernym_rows:
                            hypernym_synset = hypernym_row[0]
                            if hypernym_synset not in processed_synsets:
                                synsets_to_process.append(hypernym_synset)
                                processed_synsets.add(hypernym_synset)

                    if inferred_supertypes:
                        return inferred_supertypes

            except sqlite3.Error as e:
                print(f"Warning: Error searching in dictionary 'wnjpn': {e}")
                
        return inferred_supertypes

    def get_all_supertypes(self, node_id: str) -> set:
        """
        Recursively finds all 'is_a' supertypes for a given node.
        It handles proper nouns by first looking up their category and then
        finding the supertypes of that category.
        e.g., "東京" -> {"都市", "場所", "概念"}
        """
        normalized_node_id = _normalize_str(node_id)
        supertypes = set()
        
        # 1. Check if it's a known proper noun
        category = self.world_model.get_category_for_proper_noun(normalized_node_id)
        if category:
            supertypes.add(category)
            # Now, find supertypes of the category
            facts_to_process = [category]
        else:
            # 2. Not a known proper noun, check if it's a regular node in the graph
            if self.world_model.has_node(normalized_node_id):
                facts_to_process = [normalized_node_id]
            else:
                # 3. New word: determine if it's a proper noun or a common noun
                is_proper, ent_type = self._is_proper_noun(normalized_node_id)
                if is_proper:
                    # It's a proper noun, try to infer its category
                    inferred_categories = self._search_internal_dictionaries(normalized_node_id)
                    # For now, just pick the first one if available
                    inferred_category = next(iter(inferred_categories), None)
                    
                    if inferred_category:
                        print(f"SymbolicReasoner: Inferred '{normalized_node_id}' is a '{inferred_category}'. Storing in ProperNounStore.")
                        self.world_model.add_proper_noun(normalized_node_id, inferred_category, provenance='inferred_by_ner')
                        supertypes.add(inferred_category)
                        facts_to_process = [inferred_category]
                    else:
                        # Cannot infer category, return empty set
                        facts_to_process = []
                else:
                    # It's a common noun, search dictionaries for its supertypes
                    inferred_supertypes = self._search_internal_dictionaries(normalized_node_id)
                    # For now, we don't automatically add new common nouns to the main graph.
                    # We just return what the dictionary says.
                    return inferred_supertypes
        
        # Common logic for traversing the graph
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

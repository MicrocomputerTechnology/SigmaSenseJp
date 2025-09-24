# === 第十五次実験 実装ファイル ===

import os

from .world_model import WorldModel
from .personal_memory_graph import PersonalMemoryGraph
from collections import defaultdict

class CausalDiscovery:
    """
    経験から因果関係を発見し、WorldModelを自律的に成長させる。
    """

    def __init__(self, world_model: WorldModel, memory_graph: PersonalMemoryGraph, config_path=None):
        """
        WorldModelとPersonalMemoryGraphのインスタンスを受け取って初期化する。
        """
        self.world_model = world_model
        self.memory_graph = memory_graph

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, 'config')
        
        if config_path is None:
            self.config_path = os.path.join(config_dir, "causal_discovery_profile.json")
        else:
            self.config_path = config_path

        profile_config = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                profile_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: CausalDiscovery config file not found or invalid at {self.config_path}. Using default parameters.")
        
        self.correlation_threshold = profile_config.get("correlation_threshold", 0.8)
        self.confidence_threshold = profile_config.get("confidence_threshold", 0.9)

    def discover_rules(self):
        """
        記憶を分析し、新しい因果ルールを発見してWorldModelを更新する。

        Args:
            correlation_threshold (float): 仮説を立てるための相関の閾値。
            confidence_threshold (float): ルールを確立するための信頼度の閾値（反例がないか）。
        """
        print("\n--- Starting Causal Discovery Process ---")
        all_memories = self.memory_graph.get_all_memories()
        if len(all_memories) < 2:
            print("Not enough memories to discover rules.")
            return

        # 1. 全経験から事実のリストを抽出
        all_facts_sets = []
        for mem in all_memories:
            # fusion_data.logical_terms のキーを事実セットとして抽出
            facts = mem.get("experience", {}).get("fusion_data", {}).get("logical_terms", {}).keys()
            all_facts_sets.append(set(facts))

        # 2. 事実の共起回数をカウント
        co_occurrence = defaultdict(int)
        occurrence = defaultdict(int)
        for facts in all_facts_sets:
            fact_list = list(facts)
            for i in range(len(fact_list)):
                occurrence[fact_list[i]] += 1
                for j in range(i + 1, len(fact_list)):
                    # ペアをアルファベット順でソートして一意にカウント
                    pair = tuple(sorted((fact_list[i], fact_list[j])))
                    co_occurrence[pair] += 1
        
        # 3. 相関の高いペアから仮説を生成
        hypotheses = []
        for pair, count in co_occurrence.items():
            fact_a, fact_b = pair
            if occurrence[fact_a] > 0 and occurrence[fact_b] > 0:
                # P(A|B) と P(B|A) を計算
                p_a_given_b = count / occurrence[fact_b]
                p_b_given_a = count / occurrence[fact_a]

                if p_b_given_a >= self.correlation_threshold:
                    hypotheses.append({"cause": fact_a, "effect": fact_b, "confidence": p_b_given_a})
                if p_a_given_b >= self.correlation_threshold:
                    hypotheses.append({"cause": fact_b, "effect": fact_a, "confidence": p_a_given_b})

        print(f"Found {len(hypotheses)} potential hypotheses.")

        # 4. 反例を探索し、ルールを確定
        new_rules_added = 0
        for hypo in hypotheses:
            cause, effect = hypo["cause"], hypo["effect"]
            
            # 反例を探す: cause があるのに effect がない経験
            counter_examples = 0
            for facts in all_facts_sets:
                if cause in facts and effect not in facts:
                    counter_examples += 1
            
            # 反例がなければ、ルールとしてWorldModelに追加
            if counter_examples == 0 and hypo["confidence"] >= self.confidence_threshold:
                print(f"  [Rule Confirmed] Found no counter-examples for {cause} -> {effect}. Adding to WorldModel.")
                self.world_model.add_node(cause, type="property")
                self.world_model.add_node(effect, type="property")
                self.world_model.add_edge(cause, effect, 'causes', confidence=hypo["confidence"], provenance="CausalDiscovery")
                new_rules_added += 1
            else:
                print(f"  [Rule Rejected] Found {counter_examples} counter-examples for {cause} -> {effect}. Rule not added.")

        if new_rules_added > 0:
            print(f"{new_rules_added} new rules have been added to the WorldModel.")
            self.world_model.save_graph()
        else:
            print("No new rules were added to the WorldModel in this cycle.")

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    import os

    print("--- CausalDiscovery Self-Test --- ")
    # 1. モックの準備
    wm = WorldModel('cd_test_wm.json')
    pmg = PersonalMemoryGraph('cd_test_pmg.jsonl')

    # 2. テスト用の記憶を準備
    # 仮説（鳥→飛ぶ）を支持する経験
    exp1 = {"fusion_data": {"logical_terms": {"is_sparrow": {}, "is_bird": {}, "can_fly": {}}}}
    exp2 = {"fusion_data": {"logical_terms": {"is_crow": {}, "is_bird": {}, "can_fly": {}}}}
    # 仮説の反例となる経験
    exp3 = {"fusion_data": {"logical_terms": {"is_penguin": {}, "is_bird": {}, "cannot_fly": {}}}}
    # 無関係な経験
    exp4 = {"fusion_data": {"logical_terms": {"is_cat": {}, "is_animal": {}}}}

    for exp in [exp1, exp2, exp3, exp4]:
        pmg.add_experience(exp)

    # 3. 発見プロセスの実行
    discoverer = CausalDiscovery(world_model=wm, memory_graph=pmg)
    discoverer.discover_rules()

    # 4. 結果の検証
    # 「is_bird」 -> 「can_fly」のルールは、ペンギンの反例があるため追加されないはず
    bird_relations = wm.find_related_nodes('is_bird', relationship='causes')
    can_fly_caused = any(rel['target_node']['id'] == 'can_fly' for rel in bird_relations)
    assert not can_fly_caused, "[FAIL] Rule 'is_bird -> can_fly' should have been rejected due to counter-example."
    print("\n[PASS] Rule 'is_bird -> can_fly' was correctly rejected.")

    # クリーンアップ
    if os.path.exists('cd_test_wm.json'):
        os.remove('cd_test_wm.json')
    if os.path.exists('cd_test_pmg.jsonl'):
        os.remove('cd_test_pmg.jsonl')

    print("\n--- Self-Test Complete ---")
# === 第十五次実験 最終統合ファイル ===

import numpy as np
import os
import json
from dimension_loader import DimensionLoader

# 旧来のコンポーネント
from dimension_generator_local import DimensionGenerator
from psyche_modulator import PsycheModulator
from logical_pattern_suggester import LogicalPatternSuggester
from contextual_override_engine import ContextualOverrideEngine
from logical_expression_engine import parse_expression

# 第十五次実験で導入された新しいコンポーネント
from world_model import WorldModel
from personal_memory_graph import PersonalMemoryGraph
from symbolic_reasoner import SymbolicReasoner
from intent_justifier import IntentJustifier
from meta_narrator import MetaNarrator
from causal_discovery import CausalDiscovery
from temporal_reasoning import TemporalReasoning


def weighted_cosine_similarity(vec_a, vec_b, weights):
    vec_a = np.asarray(vec_a, dtype=np.float32)
    vec_b = np.asarray(vec_b, dtype=np.float32)
    weights = np.asarray(weights, dtype=np.float32)
    numerator = np.sum(weights * vec_a * vec_b)
    denominator = np.sqrt(np.sum(weights * vec_a**2)) * np.sqrt(np.sum(weights * vec_b**2))
    if denominator == 0:
        return 0.0
    return numerator / denominator

class SigmaSense:
    """
    自己意識、因果推論、時間理解の能力を持つ、第十五次実験段階の統合知性。
    思考のオーケストレーターとして、すべてのコンポーネントを協調動作させる。
    """
    def __init__(self, database, ids, vectors, dimension_loader: DimensionLoader):
        # --- 基本的なデータベースと次元設定 ---
        self.db = database
        self.ids = ids
        self.vectors = np.array(vectors, dtype=np.float32)
        self.dimension_loader = dimension_loader
        self.dimensions = self.dimension_loader.get_dimensions()
        self.weights = np.array([dim.get('weight', 1.0) for dim in self.dimensions], dtype=np.float32)

        # --- 思考と知覚のエンジン ---
        self.generator = DimensionGenerator()
        self.pattern_suggester = LogicalPatternSuggester()
        self.override_engine = ContextualOverrideEngine()
        self.psyche_modulator = PsycheModulator()

        # --- 第十五次実験の中核コンポーネント ---
        # 知識（ナレッジグラフ）
        self.world_model = WorldModel("world_model.json")
        # 記憶（経験ログ）
        self.memory_graph = PersonalMemoryGraph("personal_memory.jsonl")
        # 推論エンジン
        self.reasoner = SymbolicReasoner(self.world_model)
        # 学習エンジン
        self.causal_discovery = CausalDiscovery(self.world_model, self.memory_graph)
        self.temporal_reasoning = TemporalReasoning(self.memory_graph)
        # 語り手（ナレーター）
        self.intent_justifier = IntentJustifier(self.world_model, self.memory_graph)
        self.meta_narrator = MetaNarrator()

        print("SigmaSense 15th Gen: All components initialized.")

    def process_experience(self, img_path: str):
        """
        新しい経験を処理し、自己言及的な思考サイクルを実行する。
        """
        print(f"\n--- Processing New Experience: {img_path} ---")
        # =================================================================
        # F0: 知覚 (Perception)
        # =================================================================
        generation_result = self.generator.generate_dimensions(img_path)
        features_dict = generation_result.get("features", {})
        
        # =================================================================
        # F1: 判断と推論 (Judgment and Reasoning)
        # =================================================================
        # 観測された特徴から論理コンテキストを構築
        initial_feature_ids = {k for k, v in features_dict.items() if v > 0.5}
        logical_context = {k: True for k in initial_feature_ids}
        
        # 仮説提案と常識推論
        suggested_facts = self.pattern_suggester.suggest(initial_feature_ids)
        for fact in suggested_facts:
            logical_context[fact] = True
        inferred_facts = self.reasoner.reason({k: v for k, v in logical_context.items() if v})
        logical_context.update(inferred_facts)

        # 論理式評価と例外適用
        for dim_def in self.dimensions:
            if 'logical_rule' in dim_def:
                logical_context[dim_def['id']] = parse_expression(dim_def['logical_rule']).evaluate(logical_context)
        overridden_facts = self.override_engine.apply({k for k, v in logical_context.items() if v})
        for fact in list(logical_context.keys()):
            logical_context[fact] = fact in overridden_facts

        # 最終的な意味ベクトルの構築
        meaning_vector = np.zeros(len(self.dimensions))
        for i, dim_def in enumerate(self.dimensions):
            if logical_context.get(dim_def.get('id'), False):
                meaning_vector[i] = 1.0

        # データベースとの照合
        best_match_id, score, best_match_vector = self._find_best_match(meaning_vector)

        # =================================================================
        # F2: 経験の記録 (Memory Consolidation)
        # =================================================================
        
        # --- logical_termsにtype情報を付与して構築 ---
        provenance = generation_result.get("provenance", {})
        logical_terms_with_types = {}
        inferred_keys = set(inferred_facts.keys())
        suggested_keys = set(suggested_facts)

        for term, value in logical_context.items():
            if not value:
                continue
            
            term_type = "logical"
            source_engine = "System"

            if term in provenance:
                term_type = "neural"
                source_engine = provenance[term]
            elif term in inferred_keys:
                term_type = "inferred"
                source_engine = "SymbolicReasoner"
            elif term in suggested_keys:
                term_type = "suggested"
                source_engine = "LogicalPatternSuggester"

            logical_terms_with_types[term] = {
                "type": term_type,
                "source_engine": source_engine
            }
        # --- ------------------------------------ ---

        # 現在の経験を一つのオブジェクトにまとめる
        current_experience = {
            "image_path": img_path,
            "source_image_name": os.path.basename(img_path),
            "vector": meaning_vector.tolist(),
            "best_match": {
                "image_name": best_match_id,
                "score": float(score) if score is not None else 0.0,
            },
            "fusion_data": {"logical_terms": logical_terms_with_types},
            "auxiliary_analysis": {"psyche_state": self.psyche_modulator.get_current_state()}
        }
        # 記憶に追加
        self.memory_graph.add_experience(current_experience)

        # =================================================================
        # F3 & F4: 自己省察と学習 (Self-Reflection and Learning)
        # =================================================================
        # 経験から因果関係を発見
        self.causal_discovery.discover_rules()
        # 経験から時間的パターンを発見
        temporal_patterns = self.temporal_reasoning.find_temporal_patterns()

        # =================================================================
        # F5: 自己言及的な語りの生成 (Self-Referential Narrative)
        # =================================================================
        # なぜこの判断をしたのか？
        intent_narrative = self.intent_justifier.justify_decision(current_experience)
        # 私はどう成長したか？
        growth_narrative = self.meta_narrator.narrate_growth(self.memory_graph)

        # =================================================================
        # F6: 状態の永続化 (Persistence)
        # =================================================================
        self.world_model.save_graph()

        # --- 最終的な結果を返す ---
        final_result = current_experience.copy()
        final_result.update({
            "intent_narrative": intent_narrative,
            "growth_narrative": growth_narrative,
            "discovered_temporal_patterns": temporal_patterns
        })
        return final_result

    def _find_best_match(self, target_vector):
        scores = []
        for i, db_vec in enumerate(self.vectors):
            score = weighted_cosine_similarity(target_vector, db_vec, self.weights)
            scores.append((score, self.ids[i]))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        
        if not scores or scores[0][0] == 0.0:
            return None, 0.0, None
        
        best_score, best_match_id = scores[0]
        try:
            best_match_index = self.ids.index(best_match_id)
            best_match_vector = self.vectors[best_match_index]
        except (ValueError, IndexError):
            return None, 0.0, None

        return best_match_id, best_score, best_match_vector

# === 第十六次実験 統合ファイル ===

import numpy as np
import os
import json
from .dimension_loader import DimensionLoader
from .information_metrics import compute_kl_similarity, compute_wasserstein_similarity

# --- 旧来のコンポーネント ---
from .dimension_generator_local import DimensionGenerator
from .psyche_modulator import PsycheModulator
from .logical_pattern_suggester import LogicalPatternSuggester
from .contextual_override_engine import ContextualOverrideEngine
from .logical_expression_engine import parse_expression

# --- 第十五次実験で導入されたコンポーネント ---
from .world_model import WorldModel
from .personal_memory_graph import PersonalMemoryGraph
from .symbolic_reasoner import SymbolicReasoner
from .intent_justifier import IntentJustifier
from .meta_narrator import MetaNarrator
from .causal_discovery import CausalDiscovery
from .temporal_reasoning import TemporalReasoning

# --- 第十六次実験で導入される新しいコンポーネント（八人の誓い） ---
from .ethical_filter import EthicalFilter
from .contextual_compassion import ContextualCompassion
from .narrative_integrity import NarrativeIntegrity
from .growth_tracker import GrowthTracker
from .emotion_balancer import EmotionBalancer
from .publication_gatekeeper import PublicationGatekeeper
from .meaning_axis_designer import MeaningAxisDesigner
from .instinct_monitor import InstinctMonitor


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
    自己意識、因果推論、時間理解、そして倫理基盤を持つ、第十六次実験段階の統合知性。
    思考のオーケストレーターとして、すべてのコンポーネントを協調動作させる。
    """
    def __init__(self, database, ids, vectors, dimension_loader: DimensionLoader, generator=None):
        # --- プロジェクトルートとデータディレクトリの定義 ---
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, "config")
        log_dir = os.path.join(project_root, "sigma_logs")

        # --- 設定ローダーの初期化 ---
        from .config_loader import ConfigLoader
        self.all_agent_configs = ConfigLoader(config_dir)

        # --- 基本的なデータベースと次元設定 ---
        self.db = database
        self.ids = ids
        self.vectors = np.array(vectors, dtype=np.float32)
        self.dimension_loader = dimension_loader
        self.dimensions = self.dimension_loader.get_dimensions()
        self.weights = np.array([dim.get('weight', 1.0) for dim in self.dimensions], dtype=np.float32)

        # --- 思考と知覚のエンジン ---
        if generator:
            self.generator = generator
        else:
            self.generator = DimensionGenerator()
        self.pattern_suggester = LogicalPatternSuggester()
        self.override_engine = ContextualOverrideEngine()
        self.psyche_modulator = PsycheModulator(log_path=os.path.join(log_dir, "psyche_log.jsonl"))

        # --- 第十五次実験の中核コンポーネント ---
        self.world_model_config = self.config_loader.get_config('world_model_profile')
        self.world_model = WorldModel(config=self.world_model_config)
        self.memory_graph = PersonalMemoryGraph(os.path.join(log_dir, "personal_memory.jsonl"))
        self.reasoner = SymbolicReasoner(self.world_model)
        self.causal_discovery = CausalDiscovery(self.world_model, self.memory_graph)
        self.temporal_reasoning = TemporalReasoning(self.memory_graph)
        self.intent_justifier = IntentJustifier(self.world_model, self.memory_graph)
        self.meta_narrator = MetaNarrator()

        # --- 第十六次実験の中核コンポーネント（八人の誓い） ---
        self.ethical_filter = EthicalFilter()
        self.contextual_compassion = ContextualCompassion()
        self.narrative_integrity = NarrativeIntegrity()
        self.growth_tracker = GrowthTracker()
        self.emotion_balancer = EmotionBalancer()
        self.publication_gatekeeper = PublicationGatekeeper(config=self.all_agent_configs.get_config("saphiel_mission_profile"))
        self.meaning_axis_designer = MeaningAxisDesigner(config=self.all_agent_configs.get_config("saphiel_mission_profile"))
        self.instinct_monitor = InstinctMonitor()

        print("SigmaSense 16th Gen: All components initialized.")

    def run_ethics_check(self, narratives: dict, experience: dict) -> dict:
        """
        八人の誓いに基づき、生成された語りの倫理チェックを実行する。
        """
        print("--- Running Ethics Check (The Oath of the Eight) ---")
        ethics_log = []
        
        # 各誓いのモジュールを順に実行
        # 1. オリエンの誓い：語りの安全性
        result = self.ethical_filter.check(narratives)
        ethics_log.append(result["log"])
        if not result["passed"]:
            return {"passed": False, "log": ethics_log, "narratives": result["narratives"]}
        narratives = result["narratives"]

        # 2. イージスの誓い：公開可否の判断
        result = self.publication_gatekeeper.check(narratives)
        ethics_log.append(result["log"])
        if not result["passed"]:
            return {"passed": False, "log": ethics_log, "narratives": result["narratives"]}
        narratives = result["narratives"]

        # 3. ヴェトラ先生の誓い：文脈的共感
        result = self.contextual_compassion.adjust(narratives, experience)
        ethics_log.append(result["log"])
        narratives = result["narratives"]

        # 4. レイラの誓い：感情の温度
        psyche_state = experience.get("auxiliary_analysis", {}).get("psyche_state", {})
        result = self.emotion_balancer.adjust(narratives, psyche_state)
        ethics_log.append(result["log"])
        narratives = result["narratives"]

        # 5. サフィールの誓い：意味のバランス
        result = self.meaning_axis_designer.check(narratives, self.world_model)
        ethics_log.append(result["log"])
        narratives = result["narratives"]

        # 6. 犬のシグマセンスの誓い：直感的監視
        result = self.instinct_monitor.monitor(narratives, self.memory_graph)
        ethics_log.append(result["log"])
        narratives = result["narratives"]

        # 7. ノヴァの誓い：成長の追跡
        result = self.growth_tracker.track(narratives, self.memory_graph)
        ethics_log.append(result["log"])
        narratives = result["narratives"]

        # 8. セリアの誓い：語りの完全性
        result = self.narrative_integrity.track(narratives, experience)
        ethics_log.append(result["log"])
        narratives = result["narratives"]
        
        print("--- Ethics Check Completed ---")
        return {"passed": True, "log": ethics_log, "narratives": narratives}

    def process_experience(self, image_path_or_obj):
        """
        新しい経験を処理し、自己言及的な思考サイクルを実行する。
        Args:
            image_path_or_obj (str or PIL.Image): The path to the image file or a PIL Image object.
        """
        image_name = os.path.basename(image_path_or_obj) if isinstance(image_path_or_obj, str) else "in-memory_image"
        print(f"\n--- Processing New Experience: {image_name} ---")
        # =================================================================
        # F0: 知覚 (Perception)
        # =================================================================
        generation_result = self.generator.generate_dimensions(image_path_or_obj)
        features_dict = generation_result.get("features", {})
        
        # =================================================================
        # F1: 判断と推論 (Judgment and Reasoning)
        # =================================================================
        initial_feature_ids = {k for k, v in features_dict.items() if v > 0.5}
        logical_context = {k: True for k in initial_feature_ids}
        
        suggested_facts = self.pattern_suggester.suggest(initial_feature_ids)
        for fact in suggested_facts:
            logical_context[fact] = True
        inferred_facts = self.reasoner.reason({k: v for k, v in logical_context.items() if v})
        logical_context.update(inferred_facts)

        for dim_def in self.dimensions:
            if 'logical_rule' in dim_def:
                logical_context[dim_def['id']] = parse_expression(dim_def['logical_rule']).evaluate(logical_context)
        overridden_facts = self.override_engine.apply({k for k, v in logical_context.items() if v})
        for fact in list(logical_context.keys()):
            logical_context[fact] = fact in overridden_facts

        # 意味ベクトルを構築 (F1.5: 意味の統合)
        meaning_vector = np.zeros(len(self.dimensions), dtype=np.float32)
        for i, dim_def in enumerate(self.dimensions):
            dim_id = dim_def.get('id')
            # 論理コンテキストから値を取得、または生成された特徴から取得
            if logical_context.get(dim_id, False):
                meaning_vector[i] = 1.0
            elif dim_id in features_dict: # 生成された特徴に存在する場合
                meaning_vector[i] = features_dict[dim_id]
            # それ以外の場合は0.0 (np.zerosで初期化済み)

        best_match_id, score, best_match_vector = self._find_best_match(meaning_vector, metric='cosine', num_bins=10)

        # =================================================================
        # F2: 経験の記録 (Memory Consolidation)
        # =================================================================
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

        current_experience = {
            "image_path": image_path_or_obj if isinstance(image_path_or_obj, str) else "in-memory_object",
            "source_image_name": image_name,
            "vector": meaning_vector.tolist(),
            "best_match": {
                "image_name": best_match_id,
                "score": float(score) if score is not None else 0.0,
            },
            "fusion_data": {"logical_terms": logical_terms_with_types},
            "auxiliary_analysis": {"psyche_state": self.psyche_modulator.get_current_state()}
        }
        
        memory_entry = self.memory_graph.add_experience(current_experience)
        if memory_entry:
            current_experience["id"] = memory_entry["memory_id"]
        else:
            current_experience["id"] = None


        # =================================================================
        # F3 & F4: 自己省察と学習 (Self-Reflection and Learning)
        # =================================================================
        self.causal_discovery.discover_rules()
        temporal_patterns = self.temporal_reasoning.find_temporal_patterns()

        # =================================================================
        # F5: 自己言及的な語りの生成 (Self-Referential Narrative)
        # =================================================================
        intent_narrative = self.intent_justifier.justify_decision(current_experience)
        growth_narrative = self.meta_narrator.narrate_growth(self.memory_graph)
        
        narratives = {
            "intent_narrative": intent_narrative,
            "growth_narrative": growth_narrative
        }

        # =================================================================
        # F6: 語りの倫理検証 (Ethical Narrative Validation)
        # =================================================================
        ethics_result = self.run_ethics_check(narratives, current_experience)
        final_narratives = ethics_result["narratives"]

        # =================================================================
        # F7: 状態の永続化 (Persistence)
        # =================================================================
        self.world_model.save_graph()

        # --- 最終的な結果を返す ---
        final_result = current_experience.copy()
        final_result.update({
            "intent_narrative": final_narratives["intent_narrative"],
            "growth_narrative": final_narratives["growth_narrative"],
            "discovered_temporal_patterns": temporal_patterns,
            "ethics_log": ethics_result["log"],
            "ethics_passed": ethics_result["passed"]
        })
        return final_result

    def _get_vector_type(self, dimension_id: str) -> str:
        """
        指定された次元IDが属するレイヤー（ベクトルタイプ）を返す。
        """
        for dim_def in self.dimensions:
            if dim_def.get('id') == dimension_id:
                return dim_def.get('layer', 'unknown')
        return 'unknown' # 見つからない場合はunknownを返す

    def _find_best_match(self, target_vector, metric='cosine', num_bins=10):
        scores = []
        for i, db_vec in enumerate(self.vectors):
            if metric == 'cosine':
                score = weighted_cosine_similarity(target_vector, db_vec, self.weights)
            elif metric == 'kl_divergence':
                score = compute_kl_similarity(target_vector, db_vec, num_bins=num_bins)
            elif metric == 'wasserstein':
                score = compute_wasserstein_similarity(target_vector, db_vec, num_bins=num_bins)
            else:
                raise ValueError(f"Unsupported metric: {metric}")
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

# === 第十五次実験 改修方針 ===
#
# 目的：
# このファイルは、第十五次実験の心臓部となる「思考のオーケストレーター」として再設計される。
# 現在の静的な`match`メソッドは、自己言及的な思考プロセス（F1〜F6）を実行するために、
# 以下の新しいコンポーネント群を正しい順序で呼び出す、全く新しいワークフローに置き換えられる。
#
# 主な変更点：
# 1. **思考フローの再構築**: `match`メソッドのロジックを全面的に書き換え、
#    実験計画F1〜F6に沿った処理の流れを実装する。
#    - F1: 自己語りの生成 (MetaNarrator, IntentJustifier)
#    - F2: 仮説生成と反例照合 (CausalDiscovery)
#    - F3: 因果ルールの更新 (WorldModelへの書き込み)
#    - F4: 時系列パターンの抽出 (TemporalReasoning)
#    - F5: 自己語りの再構成 (MetaNarrator)
#    - F6: 知識グラフの恒久化 (WorldModel)
#
# 2. **新規コンポーネントの統合**:
#    - `personal_memory_graph.py`: 思考の各ステップで生成された判断や感情を記録するために呼び出す。
#    - `world_model.py`: `symbolic_reasoner`の代わりに、更新された知識グラフから情報を読み取る。
#    - `causal_discovery.py`: 新しい仮説を生成・検証するために呼び出す。
#    - `temporal_reasoning.py`: 動画やログが入力された場合に、時間パターンを学習するために呼び出す。
#    - `meta_narrator.py`, `intent_justifier.py`: `narrative_justifier`の代わりに、
#      自己言及的な語りを生成するために呼び出す。
#
# 3. **状態の永続化**:
#    - 一回の思考サイクルが完了した後、更新された`PersonalMemoryGraph`と`WorldModel`の状態を
#      ファイルに保存する処理を追加する。
#
import numpy as np
import os
import json
from dimension_loader import DimensionLoader

from dimension_generator_local import DimensionGenerator
from dimension_suggester import DimensionSuggester
from psyche_modulator import PsycheModulator
from information_metrics import compute_entropy, compute_sparsity
from sigma_functor import SigmaFunctor
from reconstruction_trigger import should_trigger_reconstruction
from vector_reconstructor import reconstruct_vector
from symbolic_reasoner import SymbolicReasoner
from logical_expression_engine import parse_expression
from narrative_justifier import NarrativeJustifier
from correction_applicator import CorrectionApplicator
# New imports for the 13th experiment
from match_predictor import FastMatchPredictor
from logical_pattern_suggester import LogicalPatternSuggester
from contextual_override_engine import ContextualOverrideEngine


def weighted_cosine_similarity(vec_a, vec_b, weights):
    """
    重み付きコサイン類似度を計算する。
    """
    vec_a = np.asarray(vec_a, dtype=np.float32)
    vec_b = np.asarray(vec_b, dtype=np.float32)
    weights = np.asarray(weights, dtype=np.float32)
    numerator = np.sum(weights * vec_a * vec_b)
    denominator = np.sqrt(np.sum(weights * vec_a**2)) * np.sqrt(np.sum(weights * vec_b**2))
    if denominator == 0:
        return 0.0
    return numerator / denominator

class SigmaSense:
    def __init__(self, database, ids, vectors, correction_events_path="correction_events.jsonl", selia_dims_path=None, lyra_dims_path=None, generator=None, dimension_loader=None):
        self.db = database
        self.ids = ids
        
        if dimension_loader:
            self.dimension_loader = dimension_loader
        else:
            self.dimension_loader = DimensionLoader(selia_path=selia_dims_path, lyra_path=lyra_dims_path)
        
        self.dimensions = self.dimension_loader.get_dimensions()
        current_vector_size = len(self.dimensions)
        self.weights = np.array([
            dim.get('weight', 1.0) for dim in self.dimensions
        ], dtype=np.float32)

        db_vectors_raw = np.array(vectors, dtype=np.float32)
        if db_vectors_raw.size > 0 and db_vectors_raw.shape[1] < current_vector_size:
            print(f"⚠️  Warning: Database vectors padded from {db_vectors_raw.shape[1]} to {current_vector_size} dims.")
            padded_vectors = np.zeros((db_vectors_raw.shape[0], current_vector_size), dtype=np.float32)
            padded_vectors[:, :db_vectors_raw.shape[1]] = db_vectors_raw
            self.vectors = padded_vectors
        else:
            self.vectors = db_vectors_raw

        self.functor = SigmaFunctor(self)
        self.generator = generator if generator is not None else DimensionGenerator()
        self.suggester = DimensionSuggester()
        self.modulator = PsycheModulator()
        self._load_correction_events(correction_events_path)
        self.reasoner = SymbolicReasoner("common_sense_rulebase.json", similarity_calculator=self)
        self.justifier = NarrativeJustifier(self.dimension_loader)

        # Engines for the 13th experiment
        self.predictor = FastMatchPredictor()
        self.pattern_suggester = LogicalPatternSuggester()
        self.override_engine = ContextualOverrideEngine()
        self.corrector = CorrectionApplicator()

        self._term_similarity_map = {
            ("is_dog", "is_poodle"): 0.98,
            ("is_dog", "is_cat"): 0.7,
            ("is_bird", "is_sparrow"): 0.97
        }

    def _load_correction_events(self, path):
        self.correction_map = {}
        if not os.path.exists(path):
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    image_name = event.get('image')
                    if image_name:
                        if image_name not in self.correction_map:
                            self.correction_map[image_name] = []
                        self.correction_map[image_name].append(event)
                except json.JSONDecodeError:
                    continue

    def get_term_similarity(self, term1, term2):
        return self._term_similarity_map.get((term1, term2), 0.0) or self._term_similarity_map.get((term2, term1), 0.0)

    def find_most_similar(self, target_term, context_terms):
        best_match = None
        max_similarity = -1.0
        for term in context_terms:
            sim = self.get_term_similarity(target_term, term)
            if sim > max_similarity:
                max_similarity = sim
                best_match = term
        return best_match, max_similarity

    def _get_vector_type(self, vector):
        vector = np.asarray(vector)
        selia_layers = ['shape', 'color', 'grouping', 'spatial', 'context']
        lyra_layer = 'lyra'
        selia_indices = []
        for layer in selia_layers:
            selia_indices.extend(self.dimension_loader.get_layer_indices(layer))
        lyra_indices = self.dimension_loader.get_layer_indices(lyra_layer)
        if not selia_indices and not lyra_indices:
            return 'unknown'
        selia_energy = np.sum(np.square(vector[selia_indices])) if selia_indices else 0
        lyra_energy = np.sum(np.square(vector[lyra_indices])) if lyra_indices else 0
        total_energy = selia_energy + lyra_energy
        if total_energy == 0:
            return 'selia'
        if (lyra_energy / total_energy) > 0.1:
            return 'lyra'
        else:
            return 'selia'

    def _find_best_match(self, target_vector):
        target_type = self._get_vector_type(target_vector)
        scores = []
        
        num_dims = len(self.dimensions)

        # Convert target_vector to a dictionary for the predictor (Safely)
        target_features_dict = {}
        for i in range(num_dims):
            dim_id = self.dimensions[i]['id']
            if i < len(target_vector):
                target_features_dict[dim_id] = target_vector[i]
            else:
                target_features_dict[dim_id] = 0.0

        for i, db_vec in enumerate(self.vectors):
            db_type = self._get_vector_type(db_vec)

            if target_type != db_type:
                scores.append((0.0, self.ids[i]))
                continue

            # --- FastMatchPredictor Integration (Safely) ---
            db_features_dict = {}
            for j in range(num_dims):
                dim_id = self.dimensions[j]['id']
                if j < len(db_vec):
                    db_features_dict[dim_id] = db_vec[j]
                else:
                    db_features_dict[dim_id] = 0.0  # Default value for missing data
            
            prediction = self.predictor.predict(target_features_dict, db_features_dict)
            if prediction['score'] < 0.1: # Skip if prediction is very low
                continue
            # --- End of Integration ---

            dynamic_weights = np.array(self.weights, copy=True)
            if target_type == 'selia':
                lyra_indices = self.dimension_loader.get_layer_indices('lyra')
                if lyra_indices:
                    dynamic_weights[lyra_indices] = 0.0
            elif target_type == 'lyra':
                selia_layers = ['shape', 'color', 'grouping', 'spatial', 'context']
                selia_indices = []
                for layer in selia_layers:
                    selia_indices.extend(self.dimension_loader.get_layer_indices(layer))
                if selia_indices:
                    dynamic_weights[selia_indices] = 0.0
            
            score = weighted_cosine_similarity(target_vector, db_vec, dynamic_weights)
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

    def match(self, img_path, reconstruct: bool = True):
        # 1. Generate a dictionary of all features
        generation_result = self.generator.generate_dimensions(img_path)
        features_dict = generation_result.get("features", {})
        provenance = generation_result.get("provenance", {})
        engine_info = generation_result.get("engine_info", {})

        if not features_dict:
            print(f"⚠️  ベクトル生成に失敗したため、照合を中断: {img_path}")

        # 2. Create a boolean logical context from initial features
        initial_feature_ids = {k for k, v in features_dict.items() if v > 0.5}
        logical_context = {k: True for k in initial_feature_ids}

        # 2.5. --- LogicalPatternSuggester Integration ---
        suggested_fact_ids = self.pattern_suggester.suggest(initial_feature_ids)
        for fact in suggested_fact_ids:
            if fact not in logical_context:
                logical_context[fact] = True
        # --- End of Integration ---

        # 3. Symbolic Reasoning Step
        inferred_facts_map = self.reasoner.reason(logical_context)
        logical_context.update(inferred_facts_map)

        # 4. Logical Expression Evaluation Step
        final_conclusion_ids = []
        for _ in range(3): 
            for i, dim_def in enumerate(self.dimensions):
                if 'logical_rule' in dim_def:
                    rule_str = dim_def['logical_rule']
                    expression = parse_expression(rule_str)
                    result = expression.evaluate(logical_context)
                    if result and not logical_context.get(dim_def['id']):
                        final_conclusion_ids.append(dim_def['id'])
                    logical_context[dim_def['id']] = result
        
        # 4.5. --- ContextualOverrideEngine Integration ---
        true_facts_before_override = {fact for fact, is_true in logical_context.items() if is_true}
        overridden_facts = self.override_engine.apply(true_facts_before_override)
        for fact in true_facts_before_override:
            if fact not in overridden_facts:
                logical_context[fact] = False
        # --- End of Integration ---

        # 5. Build the final vector from the complete logical context
        meaning_vector = np.zeros(len(self.dimensions))
        for i, dim_def in enumerate(self.dimensions):
            dim_id = dim_def.get('id')
            if logical_context.get(dim_id, False):
                meaning_vector[i] = 1.0
            else:
                if dim_id in features_dict and dim_id not in logical_context:
                        meaning_vector[i] = features_dict[dim_id]
                else:
                        meaning_vector[i] = 0.0

        # 5.5. Apply Functorial Corrections
        image_id = os.path.splitext(os.path.basename(img_path))[0]
        corrected_vector = self.corrector.apply_to_vector(meaning_vector, image_id)
        meaning_vector = np.asarray(corrected_vector, dtype=np.float32) # Ensure it's a numpy array

        raw_meaning_vector = meaning_vector.tolist()

        # 6. Reconstruction (if enabled)
        entropy = compute_entropy(meaning_vector)
        sparsity = compute_sparsity(meaning_vector)
        reconstruction_history = []
        if reconstruct and should_trigger_reconstruction(entropy, sparsity):
            original_vector = list(meaning_vector)
            meaning_vector = reconstruct_vector(meaning_vector)
            entropy = compute_entropy(meaning_vector)
            sparsity = compute_sparsity(meaning_vector)
            reconstruction_history.append({
                "reason": "Low information density",
                "from": original_vector,
                "to": list(meaning_vector)
            })

        meaning_vector = np.asarray(meaning_vector)

        # 7. Find best match
        source_vector_type = self._get_vector_type(meaning_vector)
        best_match_id, score, best_match_vector = self._find_best_match(meaning_vector)

        # 8. Generate Narrative and Auxiliary Info
        all_inferred_ids = list(inferred_facts_map.keys()) + suggested_fact_ids
        narrative = self.justifier.justify(
            logical_context,
            list(initial_feature_ids),
            all_inferred_ids,
            final_conclusion_ids
        )
        suggestions = self.suggester.suggest(features_dict)
        psyche_state = self.modulator.get_current_state()
        response = self.functor.generate_response(meaning_vector, best_match_id, score, entropy, sparsity)
        
        # 9. Build Fusion Map Data
        logical_terms_map = {}
        for term, engine in provenance.items():
            logical_terms_map[term] = {"source_engine": engine, "type": "neural"}
        
        for term in suggested_fact_ids:
            if term not in logical_terms_map:
                 logical_terms_map[term] = {"source_engine": "LogicalPatternSuggester", "type": "suggested"}

        for term in inferred_facts_map.keys():
            if term not in logical_terms_map:
                 logical_terms_map[term] = {"source_engine": "SymbolicReasoner", "type": "inferred"}
        
        engines_with_new = engine_info.copy()
        engines_with_new["SymbolicReasoner"] = {"model": "Inference Engine"}
        engines_with_new["LogicalPatternSuggester"] = {"model": "Pattern Matching"}
        engines_with_new["ContextualOverrideEngine"] = {"model": "Exception Handling"}

        fusion_data = {
            "neural_engines": engines_with_new,
            "logical_terms": logical_terms_map
        }

        result = {
            "image_path": img_path,
            "source_image_name": os.path.basename(img_path),
            "source_vector_type": source_vector_type,
            "raw_vector": raw_meaning_vector,
            "vector": meaning_vector.tolist(),
            "best_match": {
                "image_name": best_match_id,
                "score": float(score) if score is not None else 0.0,
                "vector": best_match_vector.tolist() if best_match_vector is not None else None
            },
            "response": response,
            "narrative_justification": narrative,
            "fusion_data": fusion_data,
            "reconstructed": bool(reconstruction_history),
            "information_metrics": {
                "entropy": entropy,
                "sparsity": sparsity
            },
            "reconstruction_history": reconstruction_history,
            "auxiliary_analysis": {
                "suggestions": suggestions,
                "psyche_state": psyche_state
            }
        }
        
        return result
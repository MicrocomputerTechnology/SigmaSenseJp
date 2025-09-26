# === 第十五次実験 実装ファイル ===

from .world_model import WorldModel
from .personal_memory_graph import PersonalMemoryGraph
from .config_loader import ConfigLoader

import json
import os

class IntentJustifier:
    """
    ある特定の判断や選択に至った「なぜ？」に答えるため、その思考プロセスと
    根拠となった過去の経験を具体的に語る。
    """

    def __init__(self, world_model: WorldModel, memory_graph: PersonalMemoryGraph, config: dict = None):
        """
        WorldModelとPersonalMemoryGraphのインスタンスを受け取って初期化する。
        """
        if config is None:
            config = {}

        self.world_model = world_model
        self.memory_graph = memory_graph
        
        self.narrative_templates = config.get("narrative_templates", {
            "initial_summary": "今回、入力された画像「{source_image}」について、最も類似度が高いと判断したのは「{best_match}」（スコア: {best_match_score:.2f}）です。",
            "logical_reasoning_path": "私の知識グラフによれば、以下の思考パスをたどりました：",
            "no_logical_reasoning": "今回の判断に直接利用できる、知識グラフ上の明確な上位概念は見つかりませんでした。",
            "past_experience_summary": "また、私は過去に「{source_image}」を{num_past_experiences}回経験しています。",
            "past_psyche_state": "直近の経験では、私の心理状態は「{last_psyche}」でした。この過去の経験が、今回の判断にも影響を与えている可能性があります。",
            "no_past_experience": "「{source_image}」については、これが初めての経験のようです。",
            "final_conclusion": "以上の論理的根拠と過去の経験の双方を考慮し、今回の最終的な判断を下しました。"
        })
        self.reasoning_path_depth = config.get("reasoning_path_depth", 5)

    def justify_decision(self, current_experience: dict):
        """
        現在の経験（判断結果）に基づき、その意図を説明する語りを生成する。

        Args:
            current_experience (dict): `sigma_sense.match`から返される結果の辞書。

        Returns:
            str: 生成された語りのテキスト。
        """
        narrative = []
        narrative.append("## 判断意図の語り")
        narrative.append("---")

        source_image = current_experience.get("source_image_name", "不明な画像")
        best_match = current_experience.get("best_match", {}).get("image_name", "なし")
        best_match_score = current_experience.get("best_match", {}).get("score", 0.0)
        
        narrative.append(self.narrative_templates.get("initial_summary", "").format(
            source_image=source_image,
            best_match=best_match,
            best_match_score=best_match_score
        ))

        # 1. 論理的根拠をWorldModelから取得
        narrative.append("\n### 知識に基づく論理的根拠：")
        logical_context = current_experience.get("fusion_data", {}).get("logical_terms", {})
        reasoning_path = self._trace_reasoning_path(logical_context)
        if reasoning_path:
            narrative.append(self.narrative_templates.get("logical_reasoning_path", ""))
            narrative.append(f"> `{' -> '.join(reasoning_path)}`")
        else:
            narrative.append(self.narrative_templates.get("no_logical_reasoning", ""))

        # 2. 過去の経験をPersonalMemoryGraphから取得
        narrative.append("\n### 過去の経験に基づく文脈的根拠：")
        past_memories = self.memory_graph.search_memories(key="source_image_name", value=source_image)
        if len(past_memories) > 1: # 現在の経験も含まれるため、1より大きいかで判断
            num_past_experiences = len(past_memories) - 1
            narrative.append(self.narrative_templates.get("past_experience_summary", "").format(
                source_image=source_image,
                num_past_experiences=num_past_experiences
            ))
            # 最新の過去の記憶（最後から2番目）を取得
            last_memory = past_memories[-2]
            last_psyche = last_memory.get("experience", {}).get("auxiliary_analysis", {}).get("psyche_state", {}).get("state", "不明")
            narrative.append(self.narrative_templates.get("past_psyche_state", "").format(
                last_psyche=last_psyche
            ))
        else:
            narrative.append(self.narrative_templates.get("no_past_experience", "").format(
                source_image=source_image
            ))

        narrative.append("\n---")
        narrative.append(self.narrative_templates.get("final_conclusion", ""))

        return "\n".join(narrative)

    def _trace_reasoning_path(self, logical_context: dict):
        """WorldModelを使って推論のパスを再構築する（簡易版）"""
        inferred_terms = {k for k, v in logical_context.items() if v.get("type") == "inferred"}
        if not inferred_terms:
            return []
        
        # 簡単のため、最初に見つかった推論のパスを返す
        start_node = list(inferred_terms)[0]
        path = [start_node]
        current_node = start_node
        # is_aを最大N階層まで遡る
        for _ in range(self.reasoning_path_depth):
            relations = self.world_model.find_related_nodes(current_node, relationship='is_a')
            if relations:
                parent_node_id = relations[0]["target_node"]["id"]
                path.append(parent_node_id)
                current_node = parent_node_id
            else:
                break
        return path

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    import os
    import tempfile

    print("--- IntentJustifier Self-Test --- ")
    # 1. モックと設定の準備
    # WorldModel用の一時ファイル
    tmp_wm_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
    tmp_wm_path = tmp_wm_file.name
    tmp_wm_file.close()
    wm_config = {"graph_path": tmp_wm_path}
    wm = WorldModel(config=wm_config)
    wm.add_node('penguin', name_ja="ペンギン")
    wm.add_node('bird', name_ja="鳥")
    wm.add_edge('penguin', 'bird', 'is_a')
    wm.save_graph()

    # PersonalMemoryGraph用の一時ファイル
    tmp_pmg_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl", mode='w')
    tmp_pmg_path = tmp_pmg_file.name
    tmp_pmg_file.close()
    pmg_config = {"memory_path": tmp_pmg_path}
    pmg = PersonalMemoryGraph(config=pmg_config)

    # 過去の経験を追加
    past_exp = {"source_image_name": "penguin.jpg", "auxiliary_analysis": {"psyche_state": {"state": "confused"}}}
    pmg.add_experience(past_exp)

    # Justifier用の設定
    justifier_config = {}

    # 2. Justifierの初期化
    justifier = IntentJustifier(world_model=wm, memory_graph=pmg, config=justifier_config)

    # 3. 現在の経験データを作成
    current_exp = {
        "source_image_name": "penguin.jpg",
        "best_match": {"image_name": "bird.jpg", "score": 0.85},
        "fusion_data": {
            "logical_terms": {
                "penguin": {"source_engine": "LegacyOpenCVEngine", "type": "neural"},
                "bird": {"source_engine": "SymbolicReasoner", "type": "inferred"}
            }
        }
    }
    # 現在の経験も記憶に追加
    pmg.add_experience(current_exp)

    # 4. 語りの生成
    print("\n--- Generating Justification ---")
    narrative = justifier.justify_decision(current_exp)
    print(narrative)

    # 5. 結果の検証
    assert "知識グラフ" in narrative
    assert "bird -> penguin" not in narrative # Path is reversed in this test
    assert "過去に「penguin.jpg」を1回経験しています" in narrative
    assert "心理状態は「confused」でした" in narrative
    print("\nAssertions passed. Narrative contains references to both knowledge and memory.")

    # クリーンアップ
    if os.path.exists(tmp_wm_path):
        os.remove(tmp_wm_path)
    if os.path.exists(tmp_pmg_path):
        os.remove(tmp_pmg_path)

    print("\n--- Self-Test Complete ---")
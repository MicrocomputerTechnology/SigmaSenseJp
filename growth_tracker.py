# growth_tracker.py - ノヴァの誓い

import re

class GrowthTracker:
    """
    自己語りの変化と成長を記録・再構成し、語りの意味軸の変遷をログ化する。
    """
    def __init__(self):
        pass

    def _extract_concepts(self, narrative_text: str) -> set:
        """簡易的な概念抽出"""
        return set(re.split(r'\W+', narrative_text))

    def track(self, narratives: dict, memory_graph) -> dict:
        """
        今回の語りと過去の語りを比較し、成長の軌跡を記録する。
        意図の語り（intent_narrative）に新しい概念（単語）が出現したかを「成長」と見なす。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            memory_graph: PersonalMemoryGraphのインスタンス。

        Returns:
            dict: 検査結果。
        """
        past_memories = memory_graph.get_all_memories()
        
        if len(past_memories) < 2: # 比較対象となる過去の記憶がない
            return {
                "passed": True,
                "log": "Nova's Oath: Passed. Not enough history to track growth.",
                "narratives": narratives
            }

        # 今回の意図の語りから概念を抽出
        current_text = narratives.get("intent_narrative", "")
        current_concepts = self._extract_concepts(current_text)

        # 前回の意図の語りから概念を抽出
        previous_experience = past_memories[-2].get("experience", {})
        previous_text = previous_experience.get("intent_narrative", "")
        previous_concepts = self._extract_concepts(previous_text)

        # 新しい概念があるかをチェック
        new_concepts = current_concepts - previous_concepts
        
        if new_concepts:
            log_message = f"Nova's Oath: Growth detected. New concepts found in intent: {sorted(list(new_concepts))[:3]}"
        else:
            log_message = "Nova's Oath: Stagnation noted. No new concepts in intent narrative."

        return {
            "passed": True, # このモジュールは警告のみでブロックはしない
            "log": log_message,
            "narratives": narratives
        }

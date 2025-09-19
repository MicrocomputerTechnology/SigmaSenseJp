# growth_tracker.py - ノヴァの誓い

import spacy

class GrowthTracker:
    """
    自己語りの変化と成長を記録・再構成し、語りの意味軸の変遷をログ化する。
    """
    def __init__(self):
        # GiNZAモデルのロード
        try:
            self.nlp = spacy.load('ja_ginza')
            print("GrowthTracker: GiNZA model loaded successfully.")
        except OSError:
            print("GrowthTracker: GiNZA model not found. Please run 'python -m spacy download ja_ginza'")
            self.nlp = None

    def _extract_concepts(self, narrative_text: str) -> set:
        """GiNZAを使ってテキストから主要な概念（名詞、固有名詞、動詞）を抽出する"""
        if not self.nlp or not narrative_text:
            return set()
        doc = self.nlp(narrative_text)
        # 語幹（lemma_）を基本の概念とする
        concepts = {
            token.lemma_ for token in doc 
            if token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ']
        }
        return concepts

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
        if not self.nlp:
            return {
                "passed": True,
                "log": "Nova's Oath: Skipped. GiNZA model not available.",
                "narratives": narratives
            }

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

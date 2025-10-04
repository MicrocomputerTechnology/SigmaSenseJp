from typing import Optional

# meaning_axis_designer.py - サフィールの誓い

import spacy

class MeaningAxisDesigner:
    """
    語りの意味軸が偏らないよう設計・調整する。
    語りの多様性とバランスを評価する。
    """
    def __init__(self, config: Optional[dict] = None):
        self.config = config if config is not None else {}
        self.balance_threshold = self.config.get("balance_threshold", 3)
        # GiNZAモデルのロード。初回は時間がかかる場合がある。
        try:
            self.nlp = spacy.load('ja_ginza')
            print("MeaningAxisDesigner: GiNZA model loaded successfully.")
        except OSError:
            print("MeaningAxisDesigner: GiNZA model not found. Please run 'python -m spacy download ja_ginza'")
            self.nlp = None

    def _extract_concepts(self, text: str) -> set:
        """GiNZAを使ってテキストから主要な概念（名詞、固有名詞、動詞）を抽出する"""
        if not self.nlp:
            return set()
        print("--- Analyzing text for concepts (MeaningAxisDesigner) ---")
        print(f"Text: {text}")
        doc = self.nlp(text)
        for token in doc:
            print(f"Token: {token.text}, Lemma: {token.lemma_}, POS: {token.pos_}")
        concepts = {
            token.lemma_ for token in doc 
            if token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ']
        }
        print(f"Extracted concepts: {concepts}")
        print("-----------------------------------------------------")
        return concepts

    def check(self, narratives: dict, world_model) -> dict:
        """
        語りで言及されている概念のバランスを評価する。
        GiNZAで抽出した概念がWorldModelにいくつ存在するかでバランスを判断する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            world_model: WorldModelのインスタンス。has_node()メソッドを持つことを期待。

        Returns:
            dict: 検査結果。
        """
        if not self.nlp:
            return {
                "passed": True,
                "log": "Saphire's Oath: Skipped. GiNZA model not available.",
                "narratives": narratives
            }

        full_text = narratives.get("intent_narrative", "") + " " + narratives.get("growth_narrative", "")
        
        # GiNZAで概念を抽出
        extracted_concepts = self._extract_concepts(full_text)

        # WorldModelに存在する概念をカウント
        found_concepts = {concept for concept in extracted_concepts if world_model.has_node(concept)}
        
        is_balanced = len(found_concepts) >= self.balance_threshold
        
        if is_balanced:
            log_message = f"Saphire's Oath: Passed. Narrative covers {len(found_concepts)} concepts, meeting the balance threshold."
        else:
            log_message = f"Saphire's Oath: Warning. Narrative is focused on only {len(found_concepts)} concepts, which is below the threshold of {self.balance_threshold}."

        return {
            "passed": True, # このモジュールは警告のみでブロックはしない
            "log": log_message,
            "narratives": narratives
        }

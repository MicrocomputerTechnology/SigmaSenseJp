# meaning_axis_designer.py - サフィールの誓い

import re

class MeaningAxisDesigner:
    """
    語りの意味軸が偏らないよう設計・調整する。
    語りの多様性とバランスを評価する。
    """
    def __init__(self, balance_threshold=3):
        self.balance_threshold = balance_threshold

    def check(self, narratives: dict, world_model) -> dict:
        """
        語りで言及されている概念のバランスを評価する。
        WorldModelに存在する概念が、語りの中にいくつ含まれるかをチェックする。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            world_model: WorldModelのインスタンス。get_all_node_ids()メソッドを持つことを期待。

        Returns:
            dict: 検査結果。
        """
        full_text = narratives.get("intent_narrative", "") + " " + narratives.get("growth_narrative", "")
        
        # WorldModelから既知の概念リストを取得
        # getattrで安全に呼び出し、なければ空のリストを返す
        all_known_concepts = getattr(world_model, 'get_all_node_ids', lambda: [])()

        # テキスト内に含まれる既知の概念をカウント
        found_concepts = {concept for concept in all_known_concepts if concept in full_text}
        
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

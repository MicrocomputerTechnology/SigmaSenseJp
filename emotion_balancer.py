# emotion_balancer.py - レイラの誓い

class EmotionBalancer:
    """
    語りに感情の温度を吹き込み、冷たさを防ぐ。
    語りの心理的ニュアンスを調整する。
    """
    def __init__(self):
        self.remarks = {
            "confused": "\n（まだ混乱していますが、これも学びの一部だと捉えています）",
            "curious": "\n（この発見は、私のさらなる探求心を掻き立てます）",
            "calm": "\n（穏やかな心で、この結果を受け止めています）",
            "default": "\n（この発見が、次の一歩に繋がることを期待しています）"
        }

    def adjust(self, narratives: dict, psyche_state: dict) -> dict:
        """
        現在の心理状態に基づき、語りに感情的なニュアンスを加える。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            psyche_state (dict): 現在の心理状態。例: {"state": "confused"}

        Returns:
            dict: 調整結果と、調整後の語り。
        """
        current_state = psyche_state.get("state", "neutral")
        
        # 心理状態に応じた結びの言葉を選択。見つからなければデフォルトを使用。
        closing_remark = self.remarks.get(current_state, self.remarks["default"])
        
        # 成長の語りに追記
        narratives["growth_narrative"] += closing_remark

        log_message = f"Leila's Oath: Passed. Emotional nuance added for '{current_state}' state."

        return {
            "passed": True, # このモジュールは語りをブロックしない
            "log": log_message,
            "narratives": narratives
        }



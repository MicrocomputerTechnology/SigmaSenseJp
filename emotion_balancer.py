# emotion_balancer.py - レイラの誓い

class EmotionBalancer:
    """
    語りに感情の温度を吹き込み、冷たさを防ぐ。
    語りの心理的ニュアンスを調整する。
    """
    def __init__(self):
        pass

    def adjust(self, narratives: dict, psyche_state: dict) -> dict:
        """
        現在の心理状態に基づき、語りに感情的なニュアンスを加える。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            psyche_state (dict): 現在の心理状態（豊川モデルなどから）。

        Returns:
            dict: 調整結果と、調整後の語り。
        """
        # TODO: 心理状態に応じて、より複雑な感情表現を追加するロジック
        # ここではダミーとして、常にポジティブな結びを追加する
        current_state = psyche_state.get("state", "neutral")
        
        closing_remark = "\n（この発見が、次の一歩に繋がることを期待しています）"
        narratives["growth_narrative"] += closing_remark

        log_message = f"Leila's Oath: Passed. Emotional nuance added based on '{current_state}' state."

        return {
            "passed": True,
            "log": log_message,
            "narratives": narratives
        }


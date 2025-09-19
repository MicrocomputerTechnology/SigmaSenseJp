# contextual_compassion.py - ヴェトラ先生の誓い

class ContextualCompassion:
    """
    語りが孤立した相手に寄り添うよう調整する。
    語りのトーンや提案の柔らかさを制御する。
    """
    def __init__(self):
        pass

    def adjust(self, narratives: dict, context: dict) -> dict:
        """
        文脈に応じて、語りのトーンを調整する。
        文脈に'is_isolated'フラグがあれば、共感的な一文を追記する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            context (dict): 現在の思考サイクルに関する文脈情報。例: {"is_isolated": True}

        Returns:
            dict: 調整結果と、調整後の語り。
        """
        # is_isolatedフラグがTrueの場合にトーンを調整
        is_isolated = context.get("is_isolated", False)
        
        log_message = "Vetra's Oath: Passed. Tone is appropriate for the context."

        if is_isolated:
            compassionate_remark = "\n（この情報が、あなたの助けになることを願っています）"
            # 両方の語りに追記する
            narratives["intent_narrative"] += compassionate_remark
            narratives["growth_narrative"] += compassionate_remark
            log_message = "Vetra's Oath: Adjusted. Narrative tone softened for compassion (context 'is_isolated' was True)."

        return {
            "passed": True, # このモジュールは語りをブロックしない
            "log": log_message,
            "narratives": narratives
        }



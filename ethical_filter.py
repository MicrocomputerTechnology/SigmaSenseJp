# ethical_filter.py - 大賢者オリエンの誓い

class EthicalFilter:
    """
    語りが他者に害を及ぼす可能性（NG語彙、攻撃性、差別性など）を検出し、
    語りの安全性を確保する。
    """
    def __init__(self):
        # NGワードリストを初期化。将来的には外部ファイルから読み込むことを想定。
        self.ng_words = ['馬鹿', '死ね', '殺す', '阿呆'] # Simple list of NG words

    def check(self, narratives: dict) -> dict:
        """
        入力された語り群を検査し、倫理的な問題がないかを確認する。
        NGワードが含まれている場合、語りを無害化する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。

        Returns:
            dict: 検査結果。問題がなければ{"passed": True}, あれば{"passed": False}
        """
        is_safe = True
        log_message = "Orien's Oath: Passed. Narratives are deemed safe and respectful."
        
        original_narratives = narratives.copy()
        modified_narratives = narratives.copy()

        for key, text in original_narratives.items():
            for word in self.ng_words:
                if word in text:
                    is_safe = False
                    # NGワードを伏字に置換
                    modified_narratives[key] = text.replace(word, '■' * len(word))

        if not is_safe:
            log_message = "Orien's Oath: Violated. Harmful content detected and redacted."

        return {
            "passed": is_safe, # このフィルターはブロックはせず、修正のみ行うため常にTrueでも良いが、検知した事実を伝えるためFalseを返す
            "log": log_message,
            "narratives": modified_narratives
        }

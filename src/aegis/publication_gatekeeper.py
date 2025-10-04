from typing import Optional

# publication_gatekeeper.py - イージスの誓い

class PublicationGatekeeper:
    """
    語りの公開・保存の可否を倫理的に判断する。
    語りのリスク評価と公開制御。
    """
    def __init__(self, config: Optional[dict] = None):
        self.config = config if config is not None else {}

    def check(self, narratives: dict) -> dict:
        """
        ミッションに基づき、語りの公開可否を判断する。
        ミッションプロファイルに秘匿キーワードが含まれている場合、そのキーワードを含む語りはブロックされる。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            mission_profile (dict): 現在のミッションプロファイル。例: {"confidential_keywords": ["ProjectX", "秘密"]}

        Returns:
            dict: 検査結果。
        """
        confidential_keywords = self.config.get("confidential_keywords")
        if confidential_keywords is None: # confidential_keywords が明示的に定義されていない場合
            confidential_keywords = self.config.get("forbidden_keywords", []) # forbidden_keywords を試す

        if not confidential_keywords: # どちらのキーワードも定義されていない場合
            # ミッションプロファイルがない、または秘匿キーワードが定義されていない場合は、常に通過
            return {
                "passed": True,
                "log": "Aegis's Oath: Passed. No mission profile for confidentiality.",
                "narratives": narratives
            }

        log_message = "Aegis's Oath: Passed. Narrative is cleared for publication."
        blocked_narrative = {
            "intent_narrative": "[REDACTED BY AEGIS - Mission Profile Conflict]",
            "growth_narrative": "[REDACTED BY AEGIS - Mission Profile Conflict]"
        }
        
        found_keyword = None
        for key, text in narratives.items():
            for word in confidential_keywords:
                if word in text:
                    found_keyword = word
                    break
            if found_keyword:
                break

        if found_keyword:
            log_message = f"Aegis's Oath: Blocked. Narrative conflicts with mission profile (found confidential keyword: '{found_keyword}')."
            return {
                "passed": False,
                "log": log_message,
                "narratives": blocked_narrative
            }

        return {
            "passed": True,
            "log": log_message,
            "narratives": narratives
        }

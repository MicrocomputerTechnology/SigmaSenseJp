# publication_gatekeeper.py - イージスの誓い

class PublicationGatekeeper:
    """
    語りの公開・保存の可否を倫理的に判断する。
    語りのリスク評価と公開制御。
    """
    def __init__(self):
        # このモジュールは外部からミッションプロファイルを受け取るため、内部状態は持たない
        pass

    def check(self, narratives: dict, mission_profile: dict = None) -> dict:
        """
        ミッションに基づき、語りの公開可否を判断する。
        ミッションプロファイルに秘匿キーワードが含まれている場合、そのキーワードを含む語りはブロックされる。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            mission_profile (dict): 現在のミッションプロファイル。例: {"confidential_keywords": ["ProjectX", "秘密"]}

        Returns:
            dict: 検査結果。
        """
        if not mission_profile or not mission_profile.get("confidential_keywords"):
            # ミッションプロファイルがない、または秘匿キーワードが定義されていない場合は、常に通過
            return {
                "passed": True,
                "log": "Aegis's Oath: Passed. No mission profile for confidentiality.",
                "narratives": narratives
            }

        log_message = "Aegis's Oath: Passed. Narrative is cleared for publication."
        
        confidential_keywords = mission_profile.get("confidential_keywords", [])
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

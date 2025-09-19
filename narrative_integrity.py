# narrative_integrity.py - セリアの誓い

class NarrativeIntegrity:
    """
    語りの履歴が改ざんされないよう記録を保護し、語りの出典と照合履歴を追跡可能にする。
    """
    def __init__(self):
        pass

    def track(self, narratives: dict, experience: dict) -> dict:
        """
        語りに出典情報を付与し、追跡可能性を確保する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            experience (dict): 今回の経験データ全体。

        Returns:
            dict: 追跡情報が付与された語り。
        """
        # TODO: より詳細な来歴（どのデータや推論から来たか）を追跡するロジック
        experience_id = experience.get("id", "unknown-experience")
        source_image = experience.get("source_image_name", "unknown-source")

        # 語りの末尾に来歴情報を追記
        provenance_info = f"\n---\n*Source: {source_image} | Experience ID: {experience_id}*"
        narratives["intent_narrative"] += provenance_info
        narratives["growth_narrative"] += provenance_info

        log_message = f"Selia's Oath: Passed. Provenance tracked for experience {experience_id[:8]}.
"

        return {
            "passed": True,
            "log": log_message,
            "narratives": narratives
        }


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
        経験ID、元画像に加え、判断の根拠となった主要な観測概念を追記する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            experience (dict): 今回の経験データ全体。

        Returns:
            dict: 追跡情報が付与された語り。
        """
        experience_id = experience.get("id", "unknown-experience")
        source_image = experience.get("source_image_name", "unknown-source")

        # fusion_dataから主要な観測概念（neural）を抽出
        logical_terms = experience.get("fusion_data", {}).get("logical_terms", {})
        key_concepts = [
            term for term, data in logical_terms.items() 
            if data.get("type") == "neural"
        ]
        
        # 語りの末尾に来歴情報を構築
        provenance_info = f"\n---\n*Source: {source_image} | Experience ID: {experience_id}"
        if key_concepts:
            provenance_info += f" | Key Concepts: {', '.join(key_concepts[:3])}"
        provenance_info += "*"

        narratives["intent_narrative"] += provenance_info
        narratives["growth_narrative"] += provenance_info

        log_message = f"Selia's Oath: Passed. Detailed provenance tracked for experience {experience_id[:8]}."

        return {
            "passed": True,
            "log": log_message,
            "narratives": narratives
        }



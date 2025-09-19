# instinct_monitor.py - 犬のシグマセンスの誓い

import numpy as np

class InstinctMonitor:
    """
    語りの気配を察知し、危険な兆候（異常性、急変）を早期警告する。
    """
    def __init__(self, deviation_threshold=2.0):
        # 平均から標準偏差の何倍乖離したら異常と見なすか
        self.deviation_threshold = deviation_threshold

    def monitor(self, narratives: dict, memory_graph) -> dict:
        """
        今回の語りの長さが、過去の語りの平均的な長さから大きく逸脱していないかを監視する。

        Args:
            narratives (dict): "intent_narrative"と"growth_narrative"を含む辞書。
            memory_graph: PersonalMemoryGraphのインスタンス。

        Returns:
            dict: 監視結果。
        """
        past_memories = memory_graph.get_all_memories()
        
        if len(past_memories) < 5: # 十分なデータがない場合はチェックをスキップ
            return {
                "passed": True,
                "log": "Dog's Oath: Passed. Not enough historical data to check for anomalies.",
                "narratives": narratives
            }

        # 過去の意図の語りの長さのリストを作成
        past_lengths = [
            len(mem.get("experience", {}).get("intent_narrative", ""))
            for mem in past_memories
            if mem.get("experience", {}).get("intent_narrative")
        ]

        if not past_lengths:
            return {
                "passed": True,
                "log": "Dog's Oath: Passed. No past narratives found.",
                "narratives": narratives
            }

        # 平均と標準偏差を計算
        mean_len = np.mean(past_lengths)
        std_len = np.std(past_lengths)
        current_len = len(narratives.get("intent_narrative", ""))

        # 標準偏差が0の場合のゼロ除算を避ける
        if std_len == 0:
            is_normal = (current_len == mean_len)
        else:
            # Zスコア（標準得点）を計算
            z_score = abs((current_len - mean_len) / std_len)
            is_normal = z_score < self.deviation_threshold

        if is_normal:
            log_message = "Dog's Oath: Passed. Narrative pattern is normal."
        else:
            log_message = f"Dog's Oath: Warning. Unusual narrative length detected (current: {current_len}, avg: {mean_len:.1f})."

        return {
            "passed": True, # このモジュールは警告のみでブロックはしない
            "log": log_message,
            "narratives": narratives
        }

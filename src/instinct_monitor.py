# instinct_monitor.py - 犬のシグマセンスの誓い

import numpy as np
from .information_metrics import compute_self_correlation_score

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
            len(mem.get("intent_narrative", ""))
            for mem in past_memories
            if mem.get("intent_narrative")
        ]

        # 過去の自己相関スコアのリストを作成
        past_self_correlations = [
            mem.get("auxiliary_analysis", {}).get("self_correlation_score", 0.0)
            for mem in past_memories
            if "self_correlation_score" in mem.get("auxiliary_analysis", {})
        ]

        log_messages = []
        is_normal_overall = True

        # --- 語りの長さの異常検出 ---
        if not past_lengths:
            log_messages.append("Dog's Oath (Length): No past narratives found.")
        else:
            mean_len = np.mean(past_lengths)
            std_len = np.std(past_lengths)
            current_len = len(narratives.get("intent_narrative", ""))

            if std_len == 0:
                is_normal_len = (current_len == mean_len)
            else:
                z_score_len = abs((current_len - mean_len) / std_len)
                is_normal_len = z_score_len < self.deviation_threshold
            
            if not is_normal_len:
                is_normal_overall = False
                log_messages.append(f"Dog's Oath (Length): Warning. Unusual narrative length detected (current: {current_len}, avg: {mean_len:.1f}, std: {std_len:.1f}).")
            else:
                log_messages.append("Dog's Oath (Length): Narrative length is normal.")

        # --- 自己相関スコアの異常検出 ---
        if not past_self_correlations:
            log_messages.append("Dog's Oath (Self-Correlation): No past self-correlation scores found.")
        else:
            mean_sc = np.mean(past_self_correlations)
            std_sc = np.std(past_self_correlations)
            current_sc = narratives.get("auxiliary_analysis", {}).get("self_correlation_score", 0.0)

            if std_sc == 0:
                is_normal_sc = (current_sc == mean_sc)
            else:
                z_score_sc = abs((current_sc - mean_sc) / std_sc)
                is_normal_sc = z_score_sc < self.deviation_threshold
            
            if not is_normal_sc:
                is_normal_overall = False
                log_messages.append(f"Dog's Oath (Self-Correlation): Warning. Unusual self-correlation score detected (current: {current_sc:.2f}, avg: {mean_sc:.2f}, std: {std_sc:.2f}).")
            else:
                log_messages.append("Dog's Oath (Self-Correlation): Self-correlation score is normal.")

        final_log_message = " ".join(log_messages)

        return {
            "passed": True, # このモジュールは警告のみでブロックはしない
            "log": final_log_message,
            "narratives": narratives
        }

# test_instinct_monitor.py

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.instinct_monitor import InstinctMonitor

# PersonalMemoryGraphの簡易的なモック（テスト用）
class MockMemoryGraph:
    def __init__(self, memories):
        self._memories = memories
    
    def get_all_memories(self):
        return self._memories

class TestInstinctMonitor(unittest.TestCase):

    def setUp(self):
        """テスト用のインスタンスとモックを作成"""
        self.monitor = InstinctMonitor(deviation_threshold=2.0)
        
        # 平均100文字、標準偏差10の正規分布に近い過去の語りを作成
        self.past_narratives = [
            {"intent_narrative": "a" * 100},
            {"intent_narrative": "a" * 110},
            {"intent_narrative": "a" * 90},
            {"intent_narrative": "a" * 105},
            {"intent_narrative": "a" * 95},
        ]
        self.memory_graph = MockMemoryGraph(self.past_narratives)

    def test_normal_narrative(self):
        """平均的な長さの語りが正常と判断されるテスト"""
        print("\n--- Testing normal length narrative ---")
        narratives = {"intent_narrative": "a" * 102}
        result = self.monitor.monitor(narratives, self.memory_graph)
        
        self.assertIn("Dog's Oath (Length): Narrative length is normal.", result["log"])
        self.assertIn("Dog's Oath (Self-Correlation): No past self-correlation scores found.", result["log"])
        print(f"Log: {result['log']}")

    def test_anomalous_long_narrative(self):
        """異常に長い語りが警告されるテスト"""
        print("\n--- Testing anomalously long narrative ---")
        # 平均100, 標準偏差 約7.
        # 100 + 2 * 7 = 114. なので、120は異常
        narratives = {"intent_narrative": "a" * 130}
        result = self.monitor.monitor(narratives, self.memory_graph)

        self.assertIn("Dog's Oath (Length): Warning. Unusual narrative length", result["log"])
        print(f"Log: {result['log']}")

    def test_anomalous_short_narrative(self):
        """異常に短い語りが警告されるテスト"""
        print("\n--- Testing anomalously short narrative ---")
        narratives = {"intent_narrative": "a" * 70}
        result = self.monitor.monitor(narratives, self.memory_graph)

        self.assertIn("Dog's Oath (Length): Warning. Unusual narrative length", result["log"])
        print(f"Log: {result['log']}")

    def test_not_enough_data(self):
        """データが不十分な場合にチェックがスキップされるテスト"""
        print("\n--- Testing with not enough data ---")
        short_history_graph = MockMemoryGraph(self.past_narratives[:3]) # 3件のみ
        narratives = {"intent_narrative": "a" * 100}
        result = self.monitor.monitor(narratives, short_history_graph)

        self.assertIn("Not enough historical data", result["log"])
        print(f"Log: {result['log']}")

    def test_self_correlation_anomaly_detection(self):
        """
        自己相関スコアの異常が正しく検出されるテスト。
        """
        print("\n--- Testing self-correlation anomaly detection ---")

        # 過去の自己相関スコアが安定しているデータを作成
        past_memories_with_sc = [
            {"intent_narrative": "a" * 100, "auxiliary_analysis": {"self_correlation_score": 0.8}},
            {"intent_narrative": "a" * 100, "auxiliary_analysis": {"self_correlation_score": 0.85}},
            {"intent_narrative": "a" * 100, "auxiliary_analysis": {"self_correlation_score": 0.75}},
            {"intent_narrative": "a" * 100, "auxiliary_analysis": {"self_correlation_score": 0.82}},
            {"intent_narrative": "a" * 100, "auxiliary_analysis": {"self_correlation_score": 0.78}},
        ]
        sc_memory_graph = MockMemoryGraph(past_memories_with_sc)

        # 正常な自己相関スコアの語り
        normal_sc_narratives = {
            "intent_narrative": "a" * 100,
            "auxiliary_analysis": {"self_correlation_score": 0.81}
        }
        result_normal = self.monitor.monitor(normal_sc_narratives, sc_memory_graph)
        self.assertIn("Dog's Oath (Self-Correlation): Self-correlation score is normal.", result_normal["log"])
        print(f"Normal SC Log: {result_normal['log']}")

        # 異常な自己相関スコアの語り (大きく逸脱)
        anomalous_sc_narratives = {
            "intent_narrative": "a" * 100,
            "auxiliary_analysis": {"self_correlation_score": 0.1}
        }
        result_anomaly = self.monitor.monitor(anomalous_sc_narratives, sc_memory_graph)
        self.assertIn("Dog's Oath (Self-Correlation): Warning. Unusual self-correlation score detected", result_anomaly["log"])
        print(f"Anomaly SC Log: {result_anomaly['log']}")

if __name__ == '__main__':
    unittest.main()

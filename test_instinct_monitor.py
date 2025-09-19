# test_instinct_monitor.py

import unittest
from instinct_monitor import InstinctMonitor

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
            {"experience": {"intent_narrative": "a" * 100}},
            {"experience": {"intent_narrative": "a" * 110}},
            {"experience": {"intent_narrative": "a" * 90}},
            {"experience": {"intent_narrative": "a" * 105}},
            {"experience": {"intent_narrative": "a" * 95}},
        ]
        self.memory_graph = MockMemoryGraph(self.past_narratives)

    def test_normal_narrative(self):
        """平均的な長さの語りが正常と判断されるテスト"""
        print("\n--- Testing normal length narrative ---")
        narratives = {"intent_narrative": "a" * 102}
        result = self.monitor.monitor(narratives, self.memory_graph)
        
        self.assertIn("Passed", result["log"])
        self.assertIn("normal", result["log"])
        print(f"Log: {result['log']}")

    def test_anomalous_long_narrative(self):
        """異常に長い語りが警告されるテスト"""
        print("\n--- Testing anomalously long narrative ---")
        # 平均100, 標準偏差 約7.
        # 100 + 2 * 7 = 114. なので、120は異常
        narratives = {"intent_narrative": "a" * 130}
        result = self.monitor.monitor(narratives, self.memory_graph)

        self.assertIn("Warning", result["log"])
        self.assertIn("Unusual narrative length", result["log"])
        print(f"Log: {result['log']}")

    def test_anomalous_short_narrative(self):
        """異常に短い語りが警告されるテスト"""
        print("\n--- Testing anomalously short narrative ---")
        narratives = {"intent_narrative": "a" * 70}
        result = self.monitor.monitor(narratives, self.memory_graph)

        self.assertIn("Warning", result["log"])
        self.assertIn("Unusual narrative length", result["log"])
        print(f"Log: {result['log']}")

    def test_not_enough_data(self):
        """データが不十分な場合にチェックがスキップされるテスト"""
        print("\n--- Testing with not enough data ---")
        short_history_graph = MockMemoryGraph(self.past_narratives[:3]) # 3件のみ
        narratives = {"intent_narrative": "a" * 100}
        result = self.monitor.monitor(narratives, short_history_graph)

        self.assertIn("Not enough historical data", result["log"])
        print(f"Log: {result['log']}")

if __name__ == '__main__':
    unittest.main()

# test_emotion_balancer.py

import unittest
from emotion_balancer import EmotionBalancer

class TestEmotionBalancer(unittest.TestCase):

    def setUp(self):
        """インスタンスを作成"""
        self.balancer = EmotionBalancer()
        self.base_narratives = {
            "intent_narrative": "意図の語り。",
            "growth_narrative": "成長の物語。"
        }

    def test_confused_state(self):
        """心理状態が'confused'の場合のテスト"""
        print("\n--- Testing 'confused' state ---")
        narratives = {k: v for k, v in self.base_narratives.items()} # copy
        psyche_state = {"state": "confused"}
        result = self.balancer.adjust(narratives, psyche_state)
        
        self.assertIn("confused", result["log"])
        self.assertIn("学びの一部", result["narratives"]["growth_narrative"])
        print(f"Appended text: {result['narratives']['growth_narrative'].replace(self.base_narratives['growth_narrative'], '')}")

    def test_curious_state(self):
        """心理状態が'curious'の場合のテスト"""
        print("\n--- Testing 'curious' state ---")
        narratives = {k: v for k, v in self.base_narratives.items()} # copy
        psyche_state = {"state": "curious"}
        result = self.balancer.adjust(narratives, psyche_state)

        self.assertIn("curious", result["log"])
        self.assertIn("探求心を掻き立てます", result["narratives"]["growth_narrative"])
        print(f"Appended text: {result['narratives']['growth_narrative'].replace(self.base_narratives['growth_narrative'], '')}")

    def test_default_state(self):
        """未定義の心理状態の場合にデフォルトの応答をするかのテスト"""
        print("\n--- Testing default state ---")
        narratives = {k: v for k, v in self.base_narratives.items()} # copy
        psyche_state = {"state": "unknown_state"}
        result = self.balancer.adjust(narratives, psyche_state)

        self.assertIn("unknown_state", result["log"])
        self.assertIn("次の一歩に繋がる", result["narratives"]["growth_narrative"])
        print(f"Appended text: {result['narratives']['growth_narrative'].replace(self.base_narratives['growth_narrative'], '')}")

if __name__ == '__main__':
    unittest.main()

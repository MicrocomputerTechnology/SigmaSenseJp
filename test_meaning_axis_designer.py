# test_meaning_axis_designer.py

import unittest
from meaning_axis_designer import MeaningAxisDesigner

# WorldModelの簡易的なモック（テスト用）
class MockWorldModel:
    def __init__(self, nodes):
        self._nodes = set(nodes)
    
    def get_all_node_ids(self):
        """既知のすべての概念IDを返す"""
        return self._nodes

class TestMeaningAxisDesigner(unittest.TestCase):

    def setUp(self):
        """テスト用のインスタンスとモックを作成"""
        self.designer = MeaningAxisDesigner(balance_threshold=3)
        # モックのWorldModelにテスト用の概念を登録
        self.world_model = MockWorldModel(["犬", "動物", "可愛い", "走る"])

    def test_balanced_narrative(self):
        """概念がバランス良く含まれている語りのテスト"""
        print("\n--- Testing balanced narrative ---")
        narratives = {
            "intent_narrative": "この犬は動物の一種です。",
            "growth_narrative": "犬は可愛いので、見ていて楽しい。"
        }
        result = self.designer.check(narratives, self.world_model)
        
        self.assertIn("Passed", result["log"])
        self.assertIn("covers 3 concepts", result["log"]) # 犬, 動物, 可愛いの3つ
        print(f"Log: {result['log']}")

    def test_unbalanced_narrative(self):
        """概念のバランスが偏っている語りのテスト"""
        print("\n--- Testing unbalanced narrative ---")
        narratives = {
            "intent_narrative": "この犬は犬です。",
            "growth_narrative": "犬は良い。"
        }
        result = self.designer.check(narratives, self.world_model)

        self.assertIn("Warning", result["log"])
        self.assertIn("focused on only 1 concepts", result["log"]) # 犬のみ
        print(f"Log: {result['log']}")

    def test_no_known_concepts(self):
        """既知の概念が全く含まれない語りのテスト"""
        print("\n--- Testing no known concepts ---")
        narratives = {
            "intent_narrative": "これはテストです。",
            "growth_narrative": "ペンギンは鳥。" # WorldModelにないのでカウントされない
        }
        result = self.designer.check(narratives, self.world_model)

        self.assertIn("Warning", result["log"])
        self.assertIn("focused on only 0 concepts", result["log"])
        print(f"Log: {result['log']}")

if __name__ == '__main__':
    unittest.main()

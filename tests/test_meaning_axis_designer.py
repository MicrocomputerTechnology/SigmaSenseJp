# test_meaning_axis_designer.py

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.meaning_axis_designer import MeaningAxisDesigner

# WorldModelの簡易的なモック（テスト用）
class MockWorldModel:
    def __init__(self, nodes):
        self._nodes = set(nodes)
    
    def has_node(self, node_id):
        """ノードが存在するかを確認する"""
        return node_id in self._nodes

class TestMeaningAxisDesigner(unittest.TestCase):

    def setUp(self):
        """テスト用のインスタンスとモックを作成"""
        self.designer = MeaningAxisDesigner(balance_threshold=3)
        # モックのWorldModelにテスト用の概念を登録
        # GiNZAは語幹を返すため、'可愛い'（形容詞）の語幹は'可愛い'、'走る'（動動詞）の語幹は'走る'
        self.world_model = MockWorldModel(["犬", "動物", "可愛い", "走る", "楽しい", "見る"])

    def test_balanced_narrative(self):
        """概念がバランス良く含まれている語りのテスト"""
        print("\n--- Testing balanced narrative ---")
        narratives = {
            "intent_narrative": "この犬は動物の一種です。",
            "growth_narrative": "犬は可愛いので、見ていて楽しい。"
        }
        result = self.designer.check(narratives, self.world_model)
        
        # 抽出される概念: 犬, 動物, 一種, です, 可愛い, 見る, 楽しい
        # WorldModelにあるもの: 犬, 動物, 可愛い, 見る, 楽しい (5つ)
        self.assertIn("Passed", result["log"])
        self.assertIn("covers 5 concepts", result["log"])
        print(f"Log: {result['log']}")

    def test_unbalanced_narrative(self):
        """概念のバランスが偏っている語りのテスト"""
        print("\n--- Testing unbalanced narrative ---")
        narratives = {
            "intent_narrative": "この犬は犬です。",
            "growth_narrative": "犬は良い。"
        }
        result = self.designer.check(narratives, self.world_model)

        # 抽出される概念: 犬, です, 良い
        # WorldModelにあるもの: 犬 (1つ)
        self.assertIn("Warning", result["log"])
        self.assertIn("focused on only 1 concepts", result["log"])
        print(f"Log: {result['log']}")

    def test_no_known_concepts(self):
        """既知の概念が全く含まれない語りのテスト"""
        print("\n--- Testing no known concepts ---")
        narratives = {
            "intent_narrative": "これはテストです。",
            "growth_narrative": "ペンギンは鳥。" # WorldModelにないのでカウントされない
        }
        result = self.designer.check(narratives, self.world_model)

        # 抽出される概念: これ, テスト, です, ペンギン, 鳥
        # WorldModelにあるもの: なし (0)
        self.assertIn("Warning", result["log"])
        self.assertIn("focused on only 0 concepts", result["log"])
        print(f"Log: {result['log']}")

if __name__ == '__main__':
    unittest.main()


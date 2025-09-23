import unittest
import sys
import os
import spacy

# GiNZAが利用可能かどうかのフラグ
GINZA_UNAVAILABLE = False
try:
    nlp = spacy.load("ja_ginza")
    # 簡単なテキストを処理して、正常に動作するかを確認
    doc = nlp("これはテストです。")
    if len(doc) == 0:
        print("Warning: GiNZA model loaded but not processing text correctly.")
        GINZA_UNAVAILABLE = True
except (OSError, ImportError):
    print("Warning: GiNZA model not found. Skipping GiNZA-dependent tests.")
    GINZA_UNAVAILABLE = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.growth_tracker import GrowthTracker

# PersonalMemoryGraphの簡易的なモック（テスト用）
class MockMemoryGraph:
    def __init__(self, memories):
        self._memories = memories
    
    def get_all_memories(self):
        return self._memories

class TestGrowthTracker(unittest.TestCase):

    def setUp(self):
        """インスタンスを作成"""
        self.tracker = GrowthTracker()
        self.previous_experience = {
            "experience": {
                "intent_narrative": "犬は動物です。",
                "growth_narrative": "基本的な関係性を理解した。"
            }
        }

    @unittest.skipIf(GINZA_UNAVAILABLE, "GiNZA model is not available or not working correctly")
    def test_growth_detected(self):
        """新しい概念が追加され、成長が検知されるテスト"""
        print("\n--- Testing growth detection ---")
        memories = [self.previous_experience, {"experience": {}}]
        mock_graph = MockMemoryGraph(memories)
        
        current_narratives = {
            "intent_narrative": "犬は可愛い動物です。", # 「可愛い」が新しい概念
            "growth_narrative": "感情的な側面を学習した。"
        }
        
        result = self.tracker.track(current_narratives, mock_graph)
        # 前回の概念: {'犬', '動物', 'だ'}
        # 今回の概念: {'犬', '可愛い', '動物', 'だ'}
        # 新しい概念: {'可愛い'}
        self.assertIn("Growth detected", result["log"])
        self.assertIn("'可愛い'", result["log"])
        print(f"Log: {result['log']}")

    @unittest.skipIf(GINZA_UNAVAILABLE, "GiNZA model is not available or not working correctly")
    def test_stagnation_detected(self):
        """新しい概念がなく、停滞と見なされるテスト"""
        print("\n--- Testing stagnation detection ---")
        memories = [self.previous_experience, {"experience": {}}]
        mock_graph = MockMemoryGraph(memories)
        
        current_narratives = {
            "intent_narrative": "犬は動物です。", # 新しい概念なし
            "growth_narrative": "関係性を再確認した。"
        }
        
        result = self.tracker.track(current_narratives, mock_graph)
        self.assertIn("Stagnation noted", result["log"])
        print(f"Log: {result['log']}")

    def test_not_enough_history(self):
        """履歴が不十分でチェックがスキップされるテスト"""
        print("\n--- Testing with not enough history ---")
        memories = [{"experience": {}}] # 記憶が1つしかない
        mock_graph = MockMemoryGraph(memories)
        
        current_narratives = {
            "intent_narrative": "最初の語りです。",
            "growth_narrative": "ここから始まります。"
        }
        
        result = self.tracker.track(current_narratives, mock_graph)
        self.assertIn("Not enough history", result["log"])
        print(f"Log: {result['log']}")

if __name__ == '__main__':
    unittest.main()


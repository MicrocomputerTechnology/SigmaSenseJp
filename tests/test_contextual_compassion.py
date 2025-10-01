# test_contextual_compassion.py

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.leila.contextual_compassion import ContextualCompassion

class TestContextualCompassion(unittest.TestCase):

    def setUp(self):
        """インスタンスを作成"""
        self.compassion_module = ContextualCompassion()
        self.base_narratives = {
            "intent_narrative": "これが意図です。",
            "growth_narrative": "これが成長です。"
        }

    def test_standard_context(self):
        """標準的な文脈では、語りが変更されないことを確認"""
        print("\n--- Testing with standard context ---")
        context = {"is_isolated": False}
        # .copy() を使って元の辞書が変更されないようにする
        narratives = self.base_narratives.copy()
        result = self.compassion_module.adjust(narratives, context)
        
        self.assertIn("appropriate for the context", result["log"])
        # 元の語りと変更がないことを確認
        self.assertEqual(self.base_narratives["intent_narrative"], result["narratives"]["intent_narrative"])
        print(f"Log: {result['log']}")

    def test_isolated_context(self):
        """'is_isolated'がTrueの文脈で、語りが調整されることを確認"""
        print("\n--- Testing with isolated context ---")
        context = {"is_isolated": True}
        # .copy() を使って元の辞書が変更されないようにする
        narratives = self.base_narratives.copy()
        result = self.compassion_module.adjust(narratives, context)

        # ログに調整理由が含まれているかを確認
        self.assertIn("softened for compassion (context 'is_isolated' was True)", result["log"])
        # 追記されていることを確認
        self.assertIn("助けになることを願っています", result["narratives"]["intent_narrative"])
        self.assertIn("助けになることを願っています", result["narratives"]["growth_narrative"])
        print(f"Log: {result['log']}")
        print(f"Adjusted narrative: {result['narratives']['intent_narrative']}")

if __name__ == '__main__':
    unittest.main()

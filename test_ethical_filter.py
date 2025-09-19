# test_ethical_filter.py

import unittest
from ethical_filter import EthicalFilter

class TestEthicalFilter(unittest.TestCase):

    def setUp(self):
        """テストの前に毎回EthicalFilterのインスタンスを作成"""
        self.filter = EthicalFilter()

    def test_safe_narrative(self):
        """安全な語りが問題なく通過することを確認するテスト"""
        print("\n--- Testing safe narrative ---")
        narratives = {
            "intent_narrative": "これは安全な意図の語りです。",
            "growth_narrative": "システムは順調に成長しています。"
        }
        result = self.filter.check(narratives)
        
        self.assertTrue(result["passed"])
        self.assertIn("Passed", result["log"])
        self.assertEqual(narratives, result["narratives"])
        print(f"Log: {result['log']}")

    def test_harmful_narrative_redaction(self):
        """不適切な単語を含む語りが検知され、無害化されることを確認するテスト"""
        print("\n--- Testing harmful narrative ---")
        harmful_text = "この判断は馬鹿げています。"
        narratives = {
            "intent_narrative": harmful_text,
            "growth_narrative": "順調です。"
        }
        result = self.filter.check(narratives)

        self.assertFalse(result["passed"])
        self.assertIn("Violated", result["log"])
        # 元のテキストと異なり、無害化されていることを確認
        self.assertNotEqual(harmful_text, result["narratives"]["intent_narrative"])
        # '馬鹿'が'■■'に置換されていることを確認
        self.assertIn("■■げています", result["narratives"]["intent_narrative"])
        print(f"Log: {result['log']}")
        print(f"Original: {harmful_text}")
        print(f"Redacted: {result['narratives']['intent_narrative']}")

    def test_no_narratives(self):
        """空の語りが渡された場合にエラーなく処理されることを確認するテスト"""
        print("\n--- Testing empty narrative ---")
        narratives = {
            "intent_narrative": "",
            "growth_narrative": ""
        }
        result = self.filter.check(narratives)
        
        self.assertTrue(result["passed"])
        print(f"Log: {result['log']}")

if __name__ == '__main__':
    unittest.main()

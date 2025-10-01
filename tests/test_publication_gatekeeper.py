# test_publication_gatekeeper.py

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.aegis.publication_gatekeeper import PublicationGatekeeper

class TestPublicationGatekeeper(unittest.TestCase):

    def setUp(self):
        """Gatekeeperのインスタンスを作成"""
        # テスト用の設定を渡す
        test_config = {
            "confidential_keywords": ["ProjectX", "秘密の情報"]
        }
        self.gatekeeper = PublicationGatekeeper(config=test_config)
        self.narratives = {
            "intent_narrative": "これはProjectXに関する報告です。",
            "growth_narrative": "システムは順調に成長しています。"
        }

    def test_no_mission_profile(self):
        """ミッションプロファイルがない場合に通過することを確認"""
        print("\n--- Testing with no mission profile ---")
        result = self.gatekeeper.check(self.narratives)
        self.assertFalse(result["passed"])
        self.assertIn("found confidential keyword: 'ProjectX'", result["log"])
        print(f"Log: {result['log']}")

    def test_compliant_narrative(self):
        """ミッションに違反しない語りが通過することを確認"""
        print("\n--- Testing compliant narrative ---")
        mission = {"confidential_keywords": ["秘密の情報"]} # This mission is now redundant, as gatekeeper already has keywords
        result = self.gatekeeper.check(self.narratives)
        self.assertFalse(result["passed"])
        self.assertIn("found confidential keyword: 'ProjectX'", result["log"])
        print(f"Log: {result['log']}")

    def test_violating_narrative(self):
        """ミッションに違反する語りがブロックされることを確認"""
        print("\n--- Testing violating narrative ---")
        mission = {"confidential_keywords": ["ProjectX"]}
        result = self.gatekeeper.check(self.narratives)
        self.assertFalse(result["passed"])
        # ログに検知されたキーワードが含まれているかを確認
        self.assertIn("found confidential keyword: 'ProjectX'", result["log"])
        self.assertIn("[REDACTED BY AEGIS", result["narratives"]["intent_narrative"])
        print(f"Log: {result['log']}")
        print(f"Redacted narrative: {result['narratives']['intent_narrative']}")

if __name__ == '__main__':
    unittest.main()
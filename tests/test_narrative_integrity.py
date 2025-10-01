# test_narrative_integrity.py

import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.nova.narrative_integrity import NarrativeIntegrity

class TestNarrativeIntegrity(unittest.TestCase):

    def setUp(self):
        """インスタンスを作成"""
        self.integrity_module = NarrativeIntegrity()
        self.base_narratives = {
            "intent_narrative": "意図の語り。",
            "growth_narrative": "成長の物語。"
        }

    def test_detailed_provenance(self):
        """詳細な来歴が正しく追記されるかのテスト"""
        print("\n--- Testing detailed provenance ---")
        narratives = {k: v for k, v in self.base_narratives.items()}
        experience = {
            "id": "test-exp-12345678",
            "source_image_name": "test.jpg",
            "fusion_data": {
                "logical_terms": {
                    "concept1": {"type": "neural"},
                    "concept2": {"type": "inferred"},
                    "concept3": {"type": "neural"},
                    "concept4": {"type": "neural"},
                    "concept5": {"type": "neural"},
                }
            }
        }
        
        result = self.integrity_module.track(narratives, experience)
        
        self.assertIn("Detailed provenance", result["log"])
        
        # 追記された来歴情報を取得
        appended_text = result["narratives"]["intent_narrative"].replace(self.base_narratives["intent_narrative"], "")
        
        # 各要素が含まれているかを確認
        self.assertIn("test.jpg", appended_text)
        self.assertIn("test-exp-12345678", appended_text)
        self.assertIn("Key Concepts", appended_text)
        self.assertIn("concept1", appended_text)
        self.assertIn("concept3", appended_text)
        self.assertIn("concept4", appended_text)
        self.assertNotIn("concept2", appended_text) # inferredは含まれない
        self.assertNotIn("concept5", appended_text) # 3つまで
        
        print(f"Appended provenance: {appended_text}")

    def test_no_neural_concepts(self):
        """neuralな概念がない場合のテスト"""
        print("\n--- Testing with no neural concepts ---")
        narratives = {k: v for k, v in self.base_narratives.items()}
        experience = {
            "id": "test-exp-no-neural",
            "source_image_name": "test2.jpg",
            "fusion_data": {
                "logical_terms": {
                    "concept2": {"type": "inferred"},
                }
            }
        }
        
        result = self.integrity_module.track(narratives, experience)
        appended_text = result["narratives"]["intent_narrative"].replace(self.base_narratives["intent_narrative"], "")
        
        self.assertNotIn("Key Concepts", appended_text)
        print(f"Appended provenance: {appended_text}")

if __name__ == '__main__':
    unittest.main()

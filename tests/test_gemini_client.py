import unittest
from unittest.mock import patch, MagicMock
import os
import json

# テスト対象のモジュールをインポートするために、パスを追加
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_client import GeminiClient

class TestGeminiClientFallback(unittest.TestCase):

    def setUp(self):
        """テストの前に一時的な設定ファイルを作成し、環境変数を設定"""
        self.config_path = "test_orient_profile.json"
        self.fallback_model_name = "mock/fallback-model"
        config_data = {
            "gemini_model": "mock-gemini-model",
            "fallback_local_model": self.fallback_model_name
        }
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        # ダミーのAPIキーを設定
        os.environ["GEMINI_API_KEY"] = "test-key"

    def tearDown(self):
        """テストの後に一時的な設定ファイルを削除"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    @patch('src.gemini_client.VetraLLMCore')
    @patch('google.generativeai.GenerativeModel')
    def test_query_text_fallback_on_api_error(self, MockGenerativeModel, MockVetraLLMCore):
        """Gemini APIがエラーを返した際に、ローカルLLMへのフォールバックが正しく機能するかをテスト"""
        # --- Arrange --- 
        # Gemini APIのモックを設定し、例外を発生させる
        mock_gemini_model_instance = MockGenerativeModel.return_value
        mock_gemini_model_instance.generate_content.side_effect = Exception("Simulated API Error")

        # VetraLLMCore（フォールバックLLM）のモックを設定
        mock_vetra_instance = MockVetraLLMCore.return_value
        mock_vetra_instance._call_local_llm.return_value = ("Fallback successful", None)

        # テスト対象のクライアントをインスタンス化
        client = GeminiClient(config_path=self.config_path)
        
        # --- Act ---
        prompt = "Test prompt"
        response = client.query_text(prompt)

        # --- Assert ---
        # 1. Gemini APIが呼び出されたことを確認
        mock_gemini_model_instance.generate_content.assert_called_once_with(prompt)

        # 2. フォールバック用のVetraLLMCoreが初期化されたことを確認
        MockVetraLLMCore.assert_called_once_with(
            code_gen_model=self.fallback_model_name, 
            hf_fallback_model_name=self.fallback_model_name
        )

        # 3. VetraLLMCoreの_call_local_llmが呼び出されたことを確認
        mock_vetra_instance._call_local_llm.assert_called_once()
        
        # 4. 最終的なレスポンスがフォールバックからのものであることを確認
        self.assertEqual(response, "Fallback successful")

if __name__ == '__main__':
    unittest.main()

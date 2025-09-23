
import unittest
import os
import json
from unittest.mock import patch, MagicMock

import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
from src.generate_ai_dimensions import generate_dimensions_with_algorithms

class TestGenerateAiDimensions(unittest.TestCase):

    @patch('src.generate_ai_dimensions.GeminiClient')
    def test_generate_dimensions_with_algorithms_success(self, MockGeminiClient):
        """
        Test that the function successfully generates and saves dimensions
        when the Gemini client returns a valid JSON list.
        """
        # 1. Setup Mock
        mock_client_instance = MockGeminiClient.return_value
        mock_response = [
            {
                "id": "test_dimension",
                "name_ja": "テスト次元",
                "description": "これはテスト用の次元です。",
                "algorithm_idea": "1. 何もしない。 2. 0.5を返す。"
            }
        ]
        mock_client_instance.query_text.return_value = mock_response

        # 2. Define test parameters
        prompt = "test prompt"
        output_filepath = "test_output_dimensions.json"

        # 3. Call the function
        generate_dimensions_with_algorithms(prompt, output_filepath)

        # 4. Assertions
        # Check that the GeminiClient was initialized
        MockGeminiClient.assert_called_once()
        # Check that query_text was called with the correct prompt
        mock_client_instance.query_text.assert_called_once_with(prompt)
        # Check that the output file was created
        self.assertTrue(os.path.exists(output_filepath))
        # Check the content of the output file
        with open(output_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data, mock_response)

        # 5. Cleanup
        os.remove(output_filepath)

    @patch('src.generate_ai_dimensions.GeminiClient')
    def test_generate_dimensions_with_algorithms_api_failure(self, MockGeminiClient):
        """
        Test that the function handles the case where the Gemini client returns None.
        """
        # 1. Setup Mock
        mock_client_instance = MockGeminiClient.return_value
        mock_client_instance.query_text.return_value = None

        # 2. Define test parameters
        prompt = "test prompt"
        output_filepath = "test_output_dimensions_fail.json"

        # 3. Call the function
        generate_dimensions_with_algorithms(prompt, output_filepath)

        # 4. Assertions
        # Check that the output file was NOT created
        self.assertFalse(os.path.exists(output_filepath))

if __name__ == '__main__':
    unittest.main()

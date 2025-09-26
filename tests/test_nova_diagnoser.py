import unittest
import numpy as np
import os
import sys
import json
from collections import deque
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.nova_diagnoser import analyze_self_correlation_trends, diagnose_unrelated
from src.personal_memory_graph import PersonalMemoryGraph
from src.dimension_loader import DimensionLoader

# Mock DimensionLoader for tests
class MockDimensionLoader:
    def __init__(self):
        self._layer_map = {
            "form": [0, 1, 2],
            "color": [3, 4, 5],
            "semantic": [6, 7, 8]
        }
    
    def get_layer_indices(self, layer_name):
        return self._layer_map.get(layer_name)

    def get_dimensions(self):
        # ダミーの次元定義を返す
        return [
            {"id": "dim_form_1", "layer": "form"},
            {"id": "dim_form_2", "layer": "form"},
            {"id": "dim_form_3", "layer": "form"},
            {"id": "dim_color_1", "layer": "color"},
            {"id": "dim_color_2", "layer": "color"},
            {"id": "dim_color_3", "layer": "color"},
            {"id": "dim_semantic_1", "layer": "semantic"},
            {"id": "dim_semantic_2", "layer": "semantic"},
            {"id": "dim_semantic_3", "layer": "semantic"},
        ]

# Mock PersonalMemoryGraph for tests
class MockPersonalMemoryGraph:
    def __init__(self, memories):
        self._memories = memories

    def get_all_memories(self):
        return self._memories

class TestNovaDiagnoser(unittest.TestCase):

    @patch('tools.nova_diagnoser.dimension_loader', new_callable=MockDimensionLoader)
    def test_diagnose_unrelated_info_lack(self, mock_dim_loader):
        """
        情報不足のレイヤーが正しく診断されるかテストする。
        """
        print("\n--- Testing diagnose_unrelated_info_lack ---")
        # colorレイヤーのエネルギーが低いログエントリ
        log_entry = {
            "vector": [0.1, 0.1, 0.1,  0.01, 0.01, 0.01,  0.5, 0.5, 0.5]
        }
        diagnoses = diagnose_unrelated(log_entry)
        self.assertIn("'Color'軸の情報が不足している可能性があります", diagnoses[0])
        print(f"Diagnoses: {diagnoses}")

    @patch('tools.nova_diagnoser.dimension_loader', new_callable=MockDimensionLoader)
    def test_diagnose_unrelated_no_info_lack(self, mock_dim_loader):
        """
        情報不足がない場合に、その旨が正しく診断されるかテストする。
        """
        print("\n--- Testing diagnose_unrelated_no_info_lack ---")
        log_entry = {
            "vector": [0.1, 0.1, 0.1,  0.2, 0.2, 0.2,  0.3, 0.3, 0.3]
        }
        diagnoses = diagnose_unrelated(log_entry)
        self.assertIn("明確な情報不足の軸は見つかりませんでした", diagnoses[0])
        print(f"Diagnoses: {diagnoses}")

    def test_analyze_self_correlation_trends_no_anomaly(self):
        """
        自己相関スコアに異常がない場合に、その旨が報告されるかテストする。
        """
        print("\n--- Testing analyze_self_correlation_trends_no_anomaly ---")
        memories = []
        for i in range(15):
            memories.append({
                "experience": {
                    "auxiliary_analysis": {"self_correlation_score": 0.8 + np.random.rand() * 0.05}
                }
            })
        mock_memory_graph = MockPersonalMemoryGraph(memories)

        with self.assertLogs('nova_diagnoser', level='INFO') as cm:
            analyze_self_correlation_trends(mock_memory_graph, window_size=10, deviation_threshold=2.0)
            self.assertIn("自己相関スコアの異常トレンドは検出されませんでした", cm.output[-1])

    def test_analyze_self_correlation_trends_with_anomaly(self):
        """
        自己相関スコアに異常がある場合に、それが検出されるかテストする。
        """
        print("\n--- Testing analyze_self_correlation_trends_with_anomaly ---")
        memories = []
        for i in range(15):
            score = 0.8 + np.random.rand() * 0.05
            if i == 12: # 異常なスコアを挿入
                score = 0.1
            memories.append({
                "experience": {
                    "auxiliary_analysis": {"self_correlation_score": score}
                }
            })
        mock_memory_graph = MockPersonalMemoryGraph(memories)

        with self.assertLogs('nova_diagnoser', level='INFO') as cm:
            analyze_self_correlation_trends(mock_memory_graph, window_size=10, deviation_threshold=2.0)
            self.assertIn("自己相関スコアが異常", cm.output[-1])

    def test_analyze_self_correlation_trends_not_enough_data(self):
        """
        十分なデータがない場合にトレンド分析がスキップされるかテストする。
        """
        print("\n--- Testing analyze_self_correlation_trends_not_enough_data ---")
        memories = []
        for i in range(5):
            memories.append({
                "experience": {
                    "auxiliary_analysis": {"self_correlation_score": 0.8 + np.random.rand() * 0.05}
                }
            })
        mock_memory_graph = MockPersonalMemoryGraph(memories)

        with self.assertLogs('nova_diagnoser', level='INFO') as cm:
            analyze_self_correlation_trends(mock_memory_graph, window_size=10, deviation_threshold=2.0)
            self.assertIn("十分な履歴データがありません", cm.output[-1])

if __name__ == '__main__':
    unittest.main()

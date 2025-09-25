# === 第十五次実験 実装ファイル ===

from .personal_memory_graph import PersonalMemoryGraph
from collections import defaultdict

class TemporalReasoning:
    """
    時系列データ（経験のログ）から、時間的な順序性やパターンを学習する。
    """

    def __init__(self, memory_graph: PersonalMemoryGraph, config_path=None):
        """
        PersonalMemoryGraphのインスタンスを受け取って初期化する。
        """
        self.memory_graph = memory_graph

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_dir = os.path.join(project_root, 'config')
        
        if config_path is None:
            self.config_path = os.path.join(config_dir, "temporal_reasoning_profile.json")
        else:
            self.config_path = config_path

        profile_config = {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                profile_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: TemporalReasoning config file not found or invalid at {self.config_path}. Using default parameters.")
        
        self.min_support = profile_config.get("min_support", 2)

    def find_temporal_patterns(self):
        """
        記憶ログを分析し、頻出する連続イベントのパターンを発見する。

        Args:
            min_support (int): パターンとして見なすための最小出現回数（支持度）。

        Returns:
            list: 発見された時間的パターンのリスト。各パターンは(イベントA, イベントB)のタプル。
        """
        print("--- Finding Temporal Patterns ---")
        all_memories = self.memory_graph.get_all_memories()
        
        # 記憶は追記された順（時系列順）になっていると仮定
        if len(all_memories) < 2:
            print("Not enough memories to find patterns.")
            return []

        # イベント遷移の回数をカウント
        transitions = defaultdict(int)
        for i in range(len(all_memories) - 1):
            try:
                # ここでは簡易的に、イベントを画像のファイル名とする
                event_a = all_memories[i]["experience"]["source_image_name"]
                event_b = all_memories[i+1]["experience"]["source_image_name"]
                transitions[(event_a, event_b)] += 1
            except KeyError:
                # 必要なキーがない記憶はスキップ
                continue

        # 支持度が閾値を超えたパターンを抽出
        found_patterns = []
        for (event_a, event_b), count in transitions.items():
            if count >= self.min_support:
                print(f"  [Pattern Found] '{event_a}' -> '{event_b}' occurred {count} times.")
                found_patterns.append((event_a, event_b))
        
        if not found_patterns:
            print("No significant temporal patterns were found.")

        return found_patterns

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    import os
    import time

    print("--- TemporalReasoning Self-Test --- ")
    test_memory_path = 'tr_test_pmg.jsonl'
    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)

    # 1. 記憶モデルの準備
    pmg = PersonalMemoryGraph(memory_path=test_memory_path)

    # 2. パターンを含む一連の経験を追加
    # A -> B というパターンを3回繰り返す
    log_pattern = ["A.jpg", "B.jpg", "C.jpg", "A.jpg", "B.jpg", "D.jpg", "A.jpg", "B.jpg"]
    print(f"\nLogging experience sequence: {log_pattern}")
    for img_name in log_pattern:
        pmg.add_experience({"experience": {"source_image_name": img_name}})
        time.sleep(0.01) # タイムスタンプを確実ずらす

    # 3. パターン発見エンジンの実行
    engine = TemporalReasoning(memory_graph=pmg)
    # 3回以上出現するパターンを探す
    patterns = engine.find_temporal_patterns(min_support=3)

    # 4. 結果の検証
    expected_pattern = ("A.jpg", "B.jpg")
    assert len(patterns) == 1, f"Expected 1 pattern, but found {len(patterns)}."
    assert patterns[0] == expected_pattern, f"Expected pattern {expected_pattern}, but found {patterns[0]}."
    print(f"\n[PASS] Correctly identified the frequent pattern: {expected_pattern}")

    # クリーンアップ
    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)

    print("\n--- Self-Test Complete ---")
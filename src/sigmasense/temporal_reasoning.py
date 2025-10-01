# === 第十五次実験 実装ファイル ===

import json
import os

from src.selia.personal_memory_graph import PersonalMemoryGraph
from .config_loader import ConfigLoader
from collections import defaultdict

class TemporalReasoning:
    """
    時系列データ（経験のログ）から、時間的な順序性やパターンを学習する。
    """

    def __init__(self, memory_graph: PersonalMemoryGraph, config: dict = None):
        """
        PersonalMemoryGraphのインスタンスを受け取って初期化する。
        """
        if config is None:
            config = {}
        self.memory_graph = memory_graph
        self.min_support = config.get("min_support", 2)

    def find_temporal_patterns(self):
        """
        記憶ログを分析し、頻出する連続イベントのパターンを発見する。

        Returns:
            list: 発見された時間的パターンのリスト。各パターンは(イベントA, イベントB)のタプル。
        """
        print(f"--- Finding Temporal Patterns (min_support={self.min_support}) ---")
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
                event_a = all_memories[i]["source_image_name"]
                event_b = all_memories[i+1]["source_image_name"]
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
    import time
    import uuid
    import datetime
    from src.hoho.sqlite_knowledge_store import SQLiteStore

    print("--- TemporalReasoning Self-Test --- ")
    test_db_path = 'tr_test.sqlite'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # 1. 記憶モデルと設定の準備
    store = SQLiteStore(db_path=test_db_path)
    pmg = PersonalMemoryGraph(store=store)

    # 2. パターンを含む一連の経験を追加
    # A -> B というパターンを3回繰り返す
    log_pattern = ["A.jpg", "B.jpg", "C.jpg", "A.jpg", "B.jpg", "D.jpg", "A.jpg", "B.jpg"]
    print(f"\nLogging experience sequence: {log_pattern}")
    for img_name in log_pattern:
        experience = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_image_name": img_name
        }
        pmg.add_experience(experience)
        time.sleep(0.01) # タイムスタンプを確実ずらす

    # 3. パターン発見エンジンの実行
    # Test with a specific min_support
    engine_config = {"min_support": 3}
    engine = TemporalReasoning(memory_graph=pmg, config=engine_config)
    patterns = engine.find_temporal_patterns()

    # 4. 結果の検証
    expected_pattern = ("A.jpg", "B.jpg")
    assert len(patterns) == 1, f"Expected 1 pattern, but found {len(patterns)}."
    assert patterns[0] == expected_pattern, f"Expected pattern {expected_pattern}, but found {patterns[0]}."
    print(f"\n[PASS] Correctly identified the frequent pattern: {expected_pattern}")

    # クリーンアップ
    store.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("\n--- Self-Test Complete ---")
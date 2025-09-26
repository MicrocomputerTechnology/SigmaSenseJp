# === 第十五次実験 実装ファイル ===

from .config_loader import ConfigLoader

class PersonalMemoryGraph:
    """
    SigmaSense単体の経験（過去の照合、判断、感情、思考プロセス）を、
    時系列のログとして記録・管理する。
    """

    def __init__(self, config: dict = None):
        """
        PersonalMemoryGraphを初期化する。

        Args:
            config (dict): 設定オブジェクト。
        """
        if config is None:
            config = {}

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        log_dir = os.path.join(project_root, "sigma_logs")
        default_memory_path = os.path.join(log_dir, "personal_memory.jsonl")

        memory_path_from_config = config.get("memory_path")
        
        if memory_path_from_config:
            # If the path from config is not absolute, join it with the project root
            if not os.path.isabs(memory_path_from_config):
                self.memory_path = os.path.join(project_root, memory_path_from_config)
            else:
                self.memory_path = memory_path_from_config
        else:
            self.memory_path = default_memory_path
            
        print(f"PersonalMemoryGraph: Initialized with memory path: {self.memory_path}")

    def add_experience(self, experience_data):
        """
        新しい経験を記憶に追加する。
        経験データにメタデータを付与し、JSON Linesファイルに追記する。

        Args:
            experience_data (dict): `sigma_sense.match`から返される結果など、記録したい経験のデータ。
        
        Returns:
            dict: メタデータが付与された完全な記憶エントリー。
        """
        memory_entry = {
            "memory_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "experience": experience_data
        }

        try:
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            with open(self.memory_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(memory_entry, ensure_ascii=False) + '\n')
            print(f"PersonalMemoryGraph: Added new experience with ID {memory_entry['memory_id']}")
            return memory_entry
        except IOError as e:
            print(f"PersonalMemoryGraph: Error adding experience. Error: {e}")
            return None

    def get_all_memories(self):
        """
        記録されたすべての記憶をリストとして読み込む。

        Returns:
            list: すべての記憶エントリーのリスト。ファイルが存在しない場合は空のリスト。
        """
        if not os.path.exists(self.memory_path):
            return []
        
        memories = []
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                for line in f:
                    memories.append(json.loads(line))
            return memories
        except (IOError, json.JSONDecodeError) as e:
            print(f"PersonalMemoryGraph: Error reading memories. Error: {e}")
            return []

    def search_memories(self, key, value):
        """
        特定のキーと値を持つ経験を検索する（簡易的な実装）。

        Args:
            key (str): 検索対象のキー（例: "source_image_name"）。
            value (any): 検索する値。

        Returns:
            list: 条件に一致した記憶エントリーのリスト。
        """
        all_memories = self.get_all_memories()
        found_memories = []
        for memory in all_memories:
            # experience辞書の中を再帰的に探索する簡易的な関数
            def find_key_value(data, k, v):
                if isinstance(data, dict):
                    for dict_k, dict_v in data.items():
                        if dict_k == k and dict_v == v:
                            return True
                        if isinstance(dict_v, (dict, list)):
                            if find_key_value(dict_v, k, v):
                                return True
                elif isinstance(data, list):
                    for item in data:
                        if find_key_value(item, k, v):
                            return True
                return False

            if find_key_value(memory.get('experience', {}), key, value):
                found_memories.append(memory)
        
        return found_memories

# --- 自己テスト用のサンプルコード ---
if __name__ == '__main__':
    print("---" + " PersonalMemoryGraph Self-Test " + "---")
    
    # CI環境でも安定して動作するよう、テストファイルへの絶対パスを生成
    script_dir = os.path.dirname(__file__)
    test_memory_path = os.path.abspath(os.path.join(script_dir, 'pmg_test.jsonl'))
    test_config = {"memory_path": test_memory_path}

    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)

    # 1. 記憶モデルの初期化
    pmg = PersonalMemoryGraph(config=test_config)

    # 2. 経験の追加
    print("\n---" + " Adding Experiences " + "---")
    exp1 = {"source_image_name": "penguin.jpg", "best_match": {"image_name": "bird.jpg"}, "psyche_state": "curious"}
    exp2 = {"source_image_name": "cat.jpg", "best_match": {"image_name": "animal.jpg"}, "psyche_state": "calm"}
    exp3 = {"source_image_name": "penguin.jpg", "best_match": {"image_name": "rock.jpg"}, "psyche_state": "confused"} # 2回目のペンギン
    
    pmg.add_experience(exp1)
    pmg.add_experience(exp2)
    pmg.add_experience(exp3)

    # 3. 全記憶の読み込み
    print("\n---" + " Retrieving All Memories " + "---")
    all_mems = pmg.get_all_memories()
    print(f"Total memories found: {len(all_mems)}")
    assert len(all_mems) == 3

    # 4. 記憶の検索
    print("\n---" + " Searching Memories " + "---")
    penguin_memories = pmg.search_memories(key="source_image_name", value="penguin.jpg")
    print(f"Found {len(penguin_memories)} memories related to 'penguin.jpg'.")
    assert len(penguin_memories) == 2

    confused_memories = pmg.search_memories(key="psyche_state", value="confused")
    print(f"Found {len(confused_memories)} memories where psyche_state was 'confused'.")
    assert len(confused_memories) == 1
    assert confused_memories[0]['experience']['source_image_name'] == 'penguin.jpg'

    print("\nAll tests passed.")

    # クリーンアップ
    if os.path.exists(test_memory_path):
        os.remove(test_memory_path)
    print("\n---" + " Self-Test Complete " + "---")
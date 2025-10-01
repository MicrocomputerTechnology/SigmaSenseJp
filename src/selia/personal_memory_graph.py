# === 第十五次実験 実装ファイル (Issue #255 改修) ===

import json
import uuid
import datetime
from src.hoho.knowledge_store_base import KnowledgeStoreBase

class PersonalMemoryGraph:
    """
    SigmaSense単体の経験（過去の照合、判断、感情、思考プロセス）を、
    知識ストアを介して記録・管理する。
    """

    def __init__(self, store: KnowledgeStoreBase):
        """
        PersonalMemoryGraphを初期化する。

        Args:
            store (KnowledgeStoreBase): データベース操作を行うための知識ストアインスタンス。
        """
        self.store = store
        print(f"PersonalMemoryGraph: Initialized with a knowledge store.")

    def add_experience(self, experience_data):
        """
        新しい経験を知識ストアに追加する。

        Args:
            experience_data (dict): `sigma_sense.match`から返される結果など、記録したい経験のデータ。
        
        Returns:
            dict: メタデータが付与された完全な記憶エントリー。
        """
        # The ID and timestamp are now expected to be added by the calling service (SigmaSense)
        if 'id' not in experience_data or 'timestamp' not in experience_data:
            print("Warning: experience_data should include 'id' and 'timestamp'.")
            experience_data['id'] = experience_data.get('id', str(uuid.uuid4()))
            experience_data['timestamp'] = experience_data.get('timestamp', datetime.datetime.now(datetime.timezone.utc).isoformat())

        try:
            self.store.add_memory(experience_data)
            print(f"PersonalMemoryGraph: Added new experience with ID {experience_data['id']}")
            return experience_data
        except Exception as e:
            print(f"PersonalMemoryGraph: Error adding experience. Error: {e}")
            return None

    def get_all_memories(self):
        """
        記録されたすべての記憶をリストとして知識ストアから読み込む。

        Returns:
            list: すべての記憶エントリーのリスト。
        """
        try:
            return self.store.get_all_memories()
        except Exception as e:
            print(f"PersonalMemoryGraph: Error reading memories. Error: {e}")
            return []

    def search_memories(self, key, value):
        """
        特定のキーと値を持つ経験を検索する（簡易的な実装）。
        NOTE: This is inefficient and should be replaced with a direct DB query in the future.

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

            if find_key_value(memory, key, value):
                found_memories.append(memory)
        
        return found_memories

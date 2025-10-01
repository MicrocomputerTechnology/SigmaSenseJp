import os
import json
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hoho.sqlite_knowledge_store import SQLiteStore

def build_knowledge_store():
    """
    Reads the source JSON knowledge base and builds a new, optimized SQLite knowledge store.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    source_json_path = os.path.join(project_root, 'config', 'world_model.json')
    target_db_path = os.path.join(project_root, 'data', 'world_model.sqlite')

    print(f"--- Building Knowledge Store from {source_json_path} ---")

    # 1. 古いDBファイルが存在すれば削除
    if os.path.exists(target_db_path):
        os.remove(target_db_path)
        print(f"Removed old database at {target_db_path}")

    # 2. ソースJSONの読み込み
    if not os.path.exists(source_json_path):
        print(f"Error: Source knowledge file not found at {source_json_path}")
        return

    with open(source_json_path, 'r', encoding='utf-8') as f:
        try:
            knowledge_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading source JSON file: {e}")
            return

    # 3. 新しいSQLiteストアの初期化
    store = SQLiteStore(db_path=target_db_path)
    print(f"Initialized new SQLite store at {target_db_path}")

    # 4. ノードの移行
    nodes = knowledge_data.get('nodes', {})
    print(f"Migrating {len(nodes)} nodes...")
    for node_id, attributes in nodes.items():
        # The attributes dict already contains the id, but add_node expects it as a separate arg
        attrs_copy = attributes.copy()
        if 'id' in attrs_copy:
            del attrs_copy['id']
        store.add_node(node_id, **attrs_copy)
    print("Node migration complete.")

    # 5. エッジの移行
    edges = knowledge_data.get('edges', [])
    print(f"Migrating {len(edges)} edges...")
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        relationship = edge.get('relationship')
        if not all([source, target, relationship]):
            continue
        
        # Pop core fields from attributes
        attributes = edge.copy()
        attributes.pop('source', None)
        attributes.pop('target', None)
        attributes.pop('relationship', None)

        store.add_edge(source, target, relationship, **attributes)
    print("Edge migration complete.")

    # 6. 完了
    store.close()
    print(f"--- Knowledge Store build complete. ---")

if __name__ == '__main__':
    build_knowledge_store()

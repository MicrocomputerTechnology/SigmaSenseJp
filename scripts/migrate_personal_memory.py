import os
import json
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sqlite_knowledge_store import SQLiteStore

def migrate_personal_memory():
    """
    Reads the old personal_memory.jsonl file and migrates the data
    to the new personal_memory table in the SQLite database.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    source_jsonl_path = os.path.join(project_root, 'sigma_logs', 'personal_memory.jsonl')
    target_db_path = os.path.join(project_root, 'data', 'world_model.sqlite')

    print(f"--- Migrating Personal Memory from {source_jsonl_path} ---")

    if not os.path.exists(source_jsonl_path):
        print(f"Source file not found at {source_jsonl_path}. Nothing to migrate.")
        return

    store = SQLiteStore(db_path=target_db_path)
    print(f"Connected to SQLite store at {target_db_path}")

    migrated_count = 0
    with open(source_jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                old_entry = json.loads(line)
                
                # Flatten the old structure into the new flat structure
                experience_data = old_entry.get('experience', {})
                experience_data['id'] = old_entry.get('memory_id')
                experience_data['timestamp'] = old_entry.get('timestamp')
                
                store.add_memory(experience_data)
                migrated_count += 1
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Skipping malformed line: {line.strip()} - Error: {e}")

    store.close()
    print(f"--- Personal Memory migration complete. Migrated {migrated_count} records. ---")

if __name__ == '__main__':
    migrate_personal_memory()

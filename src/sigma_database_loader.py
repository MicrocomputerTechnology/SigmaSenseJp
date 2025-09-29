import json
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sqlite_knowledge_store import SQLiteStore

def load_sigma_database(db_path):
    """
    意味データベース（SQLite）を読み込み、ID、意味ベクトル群、レイヤー群を返す。
    """
    if not os.path.exists(db_path):
        print(f"Warning: Database file not found at {db_path}. Returning empty database.")
        return [], [], [], []

    store = SQLiteStore(db_path=db_path)
    ids, vectors, layers = store.get_all_vectors()
    store.close()

    # Reconstruct the original 'data' list of dicts for compatibility
    data = [
        {"id": i, "meaning_vector": v, "layer": l}
        for i, v, l in zip(ids, vectors, layers)
    ]

    return data, ids, vectors, layers

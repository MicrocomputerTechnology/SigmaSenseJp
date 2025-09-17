import json

def load_sigma_database(json_path):
    """
    意味データベース（JSON）を読み込み、IDと意味ベクトル群を返す。
    各エントリは {"id": ..., "meaning_vector": [...]} の形式を持つ。
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = []
    vectors = []
    for entry in data:
        ids.append(entry["id"])
        vectors.append(entry["meaning_vector"])

    return data, ids, vectors

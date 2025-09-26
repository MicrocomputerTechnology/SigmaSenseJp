import json

def load_sigma_database(json_path):
    """
    意味データベース（JSON）を読み込み、ID、意味ベクトル群、レイヤー群を返す。
    各エントリは {"id": ..., "meaning_vector": [...], "layer": "..."} の形式を持つ。
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = []
    vectors = []
    layers = []
    for entry in data:
        ids.append(entry["id"])
        vectors.append(entry["meaning_vector"])
        layers.append(entry.get("layer", "unknown")) # layerがない場合に備える

    return data, ids, vectors, layers

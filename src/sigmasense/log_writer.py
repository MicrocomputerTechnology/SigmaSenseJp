import os
import json
from datetime import datetime

LOG_DIR = "sigma_logs"

def write_log(result):
    """
    照合結果を JSON ファイルとして保存する。
    ファイル名は画像名とタイムスタンプに基づく。
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    img_name = os.path.basename(result["image_path"]).split('.')[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{img_name}_{timestamp}.json"
    path = os.path.join(LOG_DIR, fname)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return path

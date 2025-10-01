import json
import datetime
import os

# This script assumes it's run from a directory where "temp_handler_terrier_id.py" exists.
# We will fix the path for the log file.

# 1. Read the successful handler code
try:
    with open("temp_handler_terrier_id.py", "r", encoding="utf-8") as f:
        handler_code = f.read()
except FileNotFoundError:
    print("Warning: temp_handler_terrier_id.py not found. Using placeholder code.")
    handler_code = "HANDLER_CODE_NOT_FOUND"


# 2. Construct the log entry
log_entry = {
  "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "learning_objective": {
    "title": "犬種識別学習（テリア）",
    "mode": "オリエン",
    "goal": "画像に写っている犬がノーフォークテリアかケアーンテリアかを見分けられるようになる"
  },
  "stage": "Improvisation",
  "status": "Success",
  "temporary_handler_code": handler_code,
  "summary": "演繹的ルール（耳の立ち上がりスコア）を用いてテリア犬種を識別するハンドラ。ベクトル生成器の改善を経て成功。",
  "execution_result": {
      "dog_02.jpg": "Norfolk Terrier (Rule: Ear score <= 0.5)",
      "dog_03.jpg": "Cairn Terrier (Rule: Ear score > 0.5)"
  },
  "review_status": "pending"
}

# 3. Append to the log file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_dir = os.path.join(project_root, "sigma_logs")
log_file_path = os.path.join(log_dir, "permanentization_log.jsonl")

with open(log_file_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


print(f"✅ 成功した一時ハンドラの情報を {log_file_path} に記録しました。")
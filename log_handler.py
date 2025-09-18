import json
import datetime

# 1. Read the successful handler code
with open("temp_handler_terrier_id.py", "r", encoding="utf-8") as f:
    handler_code = f.read()

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
with open("permanentization_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


print("✅ 成功した一時ハンドラの情報を permanentization_log.jsonl に記録しました。")
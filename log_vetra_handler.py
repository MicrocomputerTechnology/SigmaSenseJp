import json
import datetime

# 1. Read the successful handler code
with open("/Users/miyata.fumio/ProjectRealize/temp_handler_number_id.py", "r", encoding="utf-8") as f:
    handler_code = f.read()

# 2. Construct the log entry
log_entry = {
  "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "learning_objective": {
    "title": "数字理解学習",
    "mode": "ヴェトラ",
    "goal": "内蔵LLMを駆使して数字を理解できるようになる"
  },
  "stage": "Improvisation",
  "status": "Success",
  "temporary_handler_code": handler_code,
  "summary": "ヴェトラモード（内蔵LLM）を用いて、数値リストから最大値を識別するハンドラ。",
  "execution_result": {
      "input": [14, 5, 27, 8, 3],
      "output": 27,
      "verification": "SUCCESS"
  },
  "review_status": "pending"
}

# 3. Append to the log file
with open("/Users/miyata.fumio/ProjectRealize/permanentization_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

print("✅ 成功したヴェトラモードの一時ハンドラの情報を permanentization_log.jsonl に記録しました。")

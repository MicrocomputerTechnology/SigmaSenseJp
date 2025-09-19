import json
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'sigma_logs', 'permanentization_log.jsonl')
HANDLERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'handlers')

# 語り/学習目標のタイトルを英語のファイル名に変換するためのマップ
translation_map = {
    "連鎖": "chain", "反復": "repetition", "断片": "fragment",
    "予兆": "omen", "対話": "dialogue", "協力": "cooperation",
    "侵食": "erosion", "破壊": "destruction", "ループ": "loop", "停滞": "stagnation",
    "犬種識別学習": "dog_breed_identification",
    "数字理解学習": "number_understanding",
}

def review_and_permanentize():
    """
    恒久化ログを読み込み、レビュー待ちのハンドラを対話的に処理する。
    語り・学習目標の両方のログ形式に対応。
    """
    if not os.path.exists(LOG_FILE):
        print(f"ログファイルが見つかりません: {LOG_FILE}")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_entries = [json.loads(line) for line in f]

    updated_entries = []
    changes_made = False
    pending_found = False

    for i, entry in enumerate(log_entries):
        if entry.get("review_status") == "pending":
            pending_found = True
            print("-" * 70)
            print(f"レビュー待ちのハンドラが見つかりました (ログエントリ #{i + 1})")
            
            # ログの形式（語り or 学習目標）に応じて情報を表示
            source_info = entry.get("learning_objective") or entry.get("narrative_meta", {})
            display_title = source_info.get("title") or f"{source_info.get('form')}/{source_info.get('axis')}"
            print(f"  対象: {display_title}")
            print(f"  タイムスタンプ: {entry.get('timestamp')}")
            
            print("\n--- レビュー対象のハンドラコード ---")
            print(entry.get("temporary_handler_code", "").strip())
            print("------------------------------------")

            while True:
                action = input("アクションを選択してください (a: 承認, r: 拒否, s: スキップ): ").lower()
                if action in ["a", "r", "s"]:
                    break
                print("無効な入力です。'a', 'r', 's' のいずれかを入力してください。")

            if action == 's':
                print("  -> スキップしました。")
                updated_entries.append(entry)
                continue

            changes_made = True
            if action == 'a':
                print("  -> ハンドラを承認します。")
                
                # ログ形式に応じてファイル名を生成
                filename = ""
                if "learning_objective" in entry:
                    title_jp = entry["learning_objective"].get("title", "unknown_objective")
                    handler_name_en = translation_map.get(title_jp, title_jp)
                    filename = f"handler_{handler_name_en}.py"
                elif "narrative_meta" in entry:
                    meta = entry.get("narrative_meta", {})
                    form_jp = meta.get("form", "unknown")
                    axis_jp = meta.get("axis", "unknown")
                    form_en = translation_map.get(form_jp, form_jp)
                    axis_en = translation_map.get(axis_jp, axis_jp)
                    filename = f"handler_{form_en}_{axis_en}.py"
                else:
                    print("     ❌ ログエントリの形式が不明なため、ファイル名を生成できません。")
                    updated_entries.append(entry)
                    continue

                filepath = os.path.join(HANDLERS_DIR, filename)
                if not os.path.exists(HANDLERS_DIR):
                    os.makedirs(HANDLERS_DIR)

                handler_code = entry.get("temporary_handler_code", "").strip()
                sys_path_code = "import sys\\nimport os\\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))"
                file_content = f"{sys_path_code}\n\nfrom src.temporary_handler_base import BaseHandler\n\n{handler_code}\n"

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(file_content)
                
                print(f"     -> 承認されたハンドラをファイルに保存しました: {filepath}")
                entry["review_status"] = "approved"
                entry["reviewer_comment"] = f"Approved and saved to {filename}"

            elif action == 'r':
                comment = input("  -> 拒否理由を記入してください (任意): ")
                entry["reviewer_comment"] = comment
                entry["review_status"] = "rejected"
                print("     ハンドラを拒否しました。")
            
            updated_entries.append(entry)
        else:
            updated_entries.append(entry)

    if not pending_found:
        print("レビュー待ちのハンドラはありませんでした。")
        return

    if changes_made:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for entry in updated_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\nログファイル '{LOG_FILE}' が更新されました。")
    else:
        print("\nログファイルに変更はありませんでした。")

if __name__ == "__main__":
    review_and_permanentize()
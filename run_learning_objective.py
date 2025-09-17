import json
import multiprocessing
import time
import datetime
import os
import importlib.util
import inspect
from temporary_handler_base import BaseHandler
from vetra_llm_core import VetraLLMCore # ヴェトラ先生の頭脳をインポート

# --- グローバル定義 ---
translation_map = {
    "犬種識別学習": "dog_breed_identification",
    "数字理解学習": "number_understanding",
}

# --- 恒久ハンドラの動的読み込み ---
def load_permanent_handlers(registry: dict):
    handlers_dir = "handlers"
    if not os.path.exists(handlers_dir):
        return
    print("--- 恒久ハンドラの読み込み開始 ---")
    for filename in os.listdir(handlers_dir):
        if filename.endswith(".py") and filename.startswith("handler_"):
            try:
                handler_name = filename.replace("handler_", "").replace(".py", "")
                module_name = f"handlers.{handler_name}"
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(handlers_dir, filename))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseHandler) and obj is not BaseHandler:
                        registry[handler_name] = obj()
                        print(f"  ✅ ハンドラ [{handler_name}] を {filename} から登録しました。")
            except Exception as e:
                print(f"  ❌ {filename} の読み込み中にエラーが発生しました: {e}")
    print("------------------------------------\n")

# --- サンドボックス実行環境 ---
def sandboxed_executor(handler_code: str, objective: dict, result_queue: multiprocessing.Queue):
    import inspect
    import cv2
    from RestrictedPython import compile_restricted, safe_builtins, Eval, Guards
    from RestrictedPython.PrintCollector import PrintCollector
    from temporary_handler_base import BaseHandler
    from RestrictedPython.Eval import default_guarded_getitem

    try:
        safe_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__restricted__',
            '__metaclass__': type,
            '_getiter_': Eval.default_guarded_getiter,
            '_print_': PrintCollector,
            'dict': dict,
            'cv2': cv2,
            '_unpack_sequence_': Guards.guarded_unpack_sequence,
            '_getitem_': default_guarded_getitem
        }
        safe_globals['BaseHandler'] = BaseHandler
        byte_code = compile_restricted(handler_code, filename='<inline code>', mode='exec')
        local_scope = {}
        exec(byte_code, safe_globals, local_scope)
        handler_class = None
        for name, obj in local_scope.items():
            if inspect.isclass(obj) and issubclass(obj, BaseHandler) and obj is not BaseHandler:
                handler_class = obj
                break
        if handler_class:
            handler_instance = handler_class()
            result = handler_instance.execute(objective)
            if '_print' in local_scope:
                result['printed_output'] = local_scope['_print'].text
            else:
                result['printed_output'] = ''
            result_queue.put(result)
        else:
            result_queue.put({"status": "error", "message": "有効なハンドラクラスが見つかりません。"})
    except Exception as e:
        result_queue.put({"status": "error", "message": f"サンドボックス実行エラー: {type(e).__name__}: {e}"})

# --- 構造化のためのログ記録 ---
def log_for_structuring(objective: dict, result: dict):
    print("📝 [ステージ3] 構造化プロセスに移行します。")
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "learning_objective": objective,
        "temporary_handler_code": objective.get("temporary_handler", ""),
        "execution_result": result, "review_status": "pending", "reviewer_comment": ""
    }
    try:
        log_entry["temporary_handler_code"] = objective.get("temporary_handler", "")
        with open("offline_permanentization_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        print("  - 成功した即興処理を `offline_permanentization_log.jsonl` に記録しました。")
    except Exception as e:
        print(f"   - ログ記録エラー: {e}")

# --- コアロジック: 学習目標の三段階処理 ---
handler_registry = {}
vetra = VetraLLMCore()

def process_learning_objective(objective: dict):
    print(f"\n--- 学習目標処理開始: {objective['title']} ---")
    mode = objective.get("mode")
    if mode == "オリエン": print("🧠 オリエンモード（オンライン）が選択されました。")
    elif mode == "ヴェトラ": print("💡 ヴェトラモード（オフライン）が選択されました。")
    else: print(f"⚠️ 不明なモードです: {mode}"); return

    handler_key = translation_map.get(objective['title'])

    handler = handler_registry.get(handler_key)
    if handler:
        print(f"➡️ [ステージ1] 既知の学習処理をキー '{handler_key}' で発見しました。")
        result = handler.execute(objective)
        print(f"  - 処理結果: {result}")
        return

    print(f"➡️ [ステージ1] 既知の学習処理が見つかりません (キー: {handler_key})。")
    print("➡️ [ステージ2] 即興処理に移行します...")
    
    handler_code = objective.get("temporary_handler")

    if not handler_code and mode == "ヴェトラ":
        print("  - 臨時ハンドラが見つかりません。ヴェトラ先生がコード生成を試みます...")
        task_description = objective.get("goal", "")
        if not task_description:
            print("  - 失敗: 学習目標(goal)が定義されていません。")
            return
        
        generated_code = vetra.generate_handler_code(task_description)
        if "エラー" in generated_code:
            print(f"  - 失敗: コード生成中にエラーが発生しました。 ({generated_code})")
            return
        
        print("  - ヴェトラ先生が以下のコードを生成しました:")
        print("----------------------------------------")
        print(generated_code)
        print("----------------------------------------")

        lines = generated_code.split('\n')
        sanitized_lines = [line for line in lines if not line.strip().startswith('import cv2')]
        handler_code = "\n".join(sanitized_lines)
        if handler_code != generated_code:
            print("  - (コード浄化: import cv2 を削除しました)")

        objective["temporary_handler"] = handler_code

    if handler_code:
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=sandboxed_executor, args=(handler_code, objective, result_queue))
        process.start(); process.join(timeout=15)
        if process.is_alive():
            process.terminate(); process.join()
            result = {"status": "error", "message": "実行がタイムアウトしました（15秒）。"}
        else:
            try: result = result_queue.get_nowait()
            except multiprocessing.queues.Empty: result = {"status": "error", "message": "サンドボックスから結果が返されませんでした。"}
        
        print(f"  - 処理結果: {result}")
        
        if result.get('status') == 'interpreted' or result.get('status') == 'completed':
            log_for_structuring(objective, result)
    else: 
        print("  - 臨時対応コードが見つからず、生成もできませんでした。処理を終了します。")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    load_permanent_handlers(handler_registry)

    number_understanding_objective = {
      "title": "数字理解学習",
      "mode": "ヴェトラ",
      "goal": "画像から主要な数字を抽出し、その値を返すハンドラを生成せよ。OpenCVを使って画像をグレースケールに変換し、輪郭を見つけて、その輪郭の数を数えること。",
      "image_path": "sigma_images/test_digit_8.png",
      "tools": ["内蔵LLM", "CodeGemma"],
      "log": True,
      "stage_hint": "即興から恒久化を想定"
    }

    print("==================================================================")
    print("== SigmaSense 自己拡張サイクル実証実験（オフラインコード生成）==")
    print("==================================================================")
    
    process_learning_objective(number_understanding_objective)

    print("\n--- 全ての学習目標の処理が完了しました ---")
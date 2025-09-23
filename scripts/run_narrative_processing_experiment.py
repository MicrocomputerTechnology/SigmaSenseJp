import json
import multiprocessing
import time
import datetime
import os
import importlib.util
import inspect
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporary_handler_base import BaseHandler
import RestrictedPython # Add this line

# --- グローバル定義 ---
# メタ情報を英語に変換するマップ
translation_map = {
    "連鎖": "chain", "反復": "repetition", "断片": "fragment",
    "予兆": "omen", "対話": "dialogue", "協力": "cooperation",
    "侵食": "erosion", "破壊": "destruction", "ループ": "loop", "停滞": "stagnation"
}

# --- 恒久ハンドラの動的読み込み ---
def load_permanent_handlers(registry: dict):
    """
    `handlers`ディレクトリから恒久ハンドラを動的に読み込み、レジストリに登録する。
    """
    handlers_dir = "handlers"
    if not os.path.exists(handlers_dir):
        print("--- 恒久ハンドラディレクトリが見つかりません。スキップします。 ---")
        return

    print("--- 恒久ハンドラの読み込み開始 ---")
    for filename in os.listdir(handlers_dir):
        if filename.endswith(".py") and filename.startswith("handler_"):
            try:
                # ファイル名から英語のformとaxisを抽出
                parts = filename.replace("handler_", "").replace(".py", "").split("_")
                if len(parts) == 2:
                    form_en, axis_en = parts[0], parts[1]
                    
                    # モジュールを動的にインポート
                    module_name = f"handlers.{filename.replace('.py', '')}"
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(handlers_dir, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # モジュールからハンドラクラスを検索してインスタンス化
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseHandler) and obj is not BaseHandler:
                            handler_instance = obj()
                            registry_key = (form_en, axis_en)
                            registry[registry_key] = handler_instance
                            print(f"  ✅ ハンドラ [{form_en}, {axis_en}] を {filename} から登録しました。")
            except Exception as e:
                print(f"  ❌ {filename} の読み込み中にエラーが発生しました: {e}")
    print("------------------------------------")

# --- サンドボックス実行環境の定義 (変更なし) ---
def sandboxed_executor(handler_code: str, narrative: dict, result_queue: multiprocessing.Queue):
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import inspect
    from RestrictedPython import compile_restricted, safe_builtins, Eval
    from RestrictedPython.PrintCollector import PrintCollector
    from src.temporary_handler_base import BaseHandler
    try:
        safe_globals = {
            '__builtins__': safe_builtins, '__name__': '__restricted__', '__metaclass__': type,
            '_getiter_': Eval.default_guarded_getiter, '_print_': PrintCollector, 'dict': dict,
            '_getitem_': auditing_getitem,
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
            result = handler_instance.execute(narrative)
            if '_print' in local_scope:
                result['printed_output'] = local_scope['_print'].text
            else:
                result['printed_output'] = ''
            result_queue.put(result)
        else: result_queue.put({"status": "error", "message": "有効なハンドラクラスが見つかりません。"})
    except Exception as e: result_queue.put({"status": "error", "message": f"サンドボックス実行エラー: {type(e).__name__}: {e}"})

# --- ステージ1: 処理ハンドラの登録 ---
handler_registry = {}
def handle_fragment_omen(narrative):
    print("✅ [ステージ1] 登録済みハンドラ(handle_fragment_omen)が実行されました。")
    return {"status": "processed", "handler": "handle_fragment_omen"}
handler_registry[("fragment", "omen")] = handle_fragment_omen # 英語キーで登録

# --- ステージ3: 恒久化のためのログ記録 (変更なし) ---
def log_for_permanentization(narrative: dict, result: dict):
    print("📝 [ステージ3] 恒久化ステージに移行します。")
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "narrative_meta": narrative.get("meta", {}),
        "temporary_handler_code": narrative.get("meta", {}).get("temporary_handler", ""),
        "execution_result": result, "review_status": "pending", "reviewer_comment": ""
    }
    try:
        with open("permanentization_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        print("   - 臨時ハンドラのコードと実行結果を `permanentization_log.jsonl` に記録しました。")
    except Exception as e: print(f"   - ログ記録エラー: {e}")

# --- コアロジック: 三段階処理 ---
def process_narrative(narrative):
    print(f"\n--- 語り処理開始: {json.dumps(narrative['meta'], ensure_ascii=False)} ---")
    meta_jp = narrative["meta"]
    
    # メタ情報を英語に変換してキーを生成
    form_en = translation_map.get(meta_jp.get("form"), meta_jp.get("form"))
    axis_en = translation_map.get(meta_jp.get("axis"), meta_jp.get("axis"))
    handler_key = (form_en, axis_en)

    # ステージ1
    handler = handler_registry.get(handler_key)
    if handler:
        print(f"🔑 登録済みハンドラをキー {handler_key} で発見しました。")
        result = handler.execute(narrative) # .execute()を呼び出すように統一
        print(f"   - 処理結果: {result}")
        return

    # ステージ2
    print(f"🟡 登録済みハンドラが見つかりません (キー: {handler_key})。臨時対応ステージに移行します。")
    if "temporary_handler" in meta_jp:
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=sandboxed_executor, args=(meta_jp["temporary_handler"], narrative, result_queue))
        process.start(); process.join(timeout=5)
        if process.is_alive():
            process.terminate(); process.join()
            result = {"status": "error", "message": "実行がタイムアウトしました（5秒）。"}
        else:
            try: result = result_queue.get_nowait()
            except multiprocessing.queues.Empty: result = {"status": "error", "message": "サンドボックスから結果が返されませんでした。"}
        print(f"   - 処理結果: {result}")
        if result.get('status') == 'interpreted':
            print("   - 集団心理状態 C(t) に影響を反映させます（シミュレーション）。")
            log_for_permanentization(narrative, result)
        elif result.get('status') == 'error': print("   - エラーが発生したため、恒久化はスキップされます。")
    else: print("   - 臨時対応コードが見つかりませんでした。")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # 起動時に恒久ハンドラを読み込む
    load_permanent_handlers(handler_registry)

    # --- テストケース ---
    # 1. 以前は「未知」だったが、恒久化され自動登録されたハンドラで処理される語り
    #    temporary_handlerは不要になっている点に注意
    permanentized_narrative = {
        "content": "鏡...", 
        "meta": {"form": "連鎖", "axis": "反復"}
    }

    # 2. 新しい未知の語り（ステージ2・3のテスト用）
    new_unknown_narrative = {
        "content": "光が...消える...", "meta": {
            "form": "侵食", "axis": "破壊",
            "temporary_handler": """\nclass ErosionHandler(BaseHandler):
    def execute(self, narrative: dict) -> dict:
        return {\"status\": \"interpreted\", \"processed_content\": \"...無になった...\"}
"""
    }}

    print("==================================================================")
    print("== SigmaSense 第十次実証実験：自己拡張ループの統合テスト ==")
    print("==================================================================")

    process_narrative(permanentized_narrative)
    process_narrative(new_unknown_narrative)
    
    print("\n--- 実験終了 ---")======================")
    print("== SigmaSense 第十次実証実験：自己拡張ループの統合テスト ==")
    print("==================================================================")

    process_narrative(permanentized_narrative)
    process_narrative(new_unknown_narrative)
    
    print("\n--- 実験終了 ---")
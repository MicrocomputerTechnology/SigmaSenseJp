import json
import os
import numpy as np

# 定数
FAILURE_LOG_PATH = "functor_consistency_failures.jsonl"
SOURCE_DB_PATH = "sigma_product_database_custom_ai_generated.json"
STABILIZED_DB_PATH = "sigma_product_database_stabilized.json"
ALPHA = 0.5 # 補正係数

def stabilize_database():
    """失敗ログに基づいてデータベースを安定化させる"""
    print("🌿 差分補正によるデータベース安定化を開始します...")

    # 1. ソースとなるデータベースを読み込む
    try:
        with open(SOURCE_DB_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    except FileNotFoundError:
        print(f"❗ エラー: ソースデータベースが見つかりません: {SOURCE_DB_PATH}")
        return
    except json.JSONDecodeError:
        print(f"❗ エラー: ソースデータベースのJSON形式が不正です: {SOURCE_DB_PATH}")
        return

    # 扱いやすいようにIDをキーにした辞書に変換
    db_dict = {item['id']: item for item in db_data}

    # 2. 失敗ログを読み込んで補正処理を行う
    try:
        with open(FAILURE_LOG_PATH, 'r', encoding='utf-8') as f:
            failure_logs = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"❗ エラー: 失敗ログファイルが見つかりません: {FAILURE_LOG_PATH}")
        print("   先に functor_consistency_checker.py を実行してください。")
        return

    if not failure_logs:
        print("✅ 失敗ログはありませんでした。データベースは既に安定的です。")
        return

    print(f"📝 {len(failure_logs)}件の失敗ログを読み込みました。補正処理を実行します。")

    for log in failure_logs:
        image_name = log.get('image')
        if not image_name:
            continue

        item_id = os.path.splitext(image_name)[0]

        if item_id in db_dict:
            # 補正対象のベクトル
            original_vector = np.array(db_dict[item_id]['meaning_vector'])
            corrected_vector = original_vector.copy()

            # 予期せず変化した次元を特定
            changed_indices = set(log.get('changed_indices', []))
            expected_indices = set(log.get('expected_indices', []))
            unexpected_indices = list(changed_indices - expected_indices)
            vector_diff = np.array(log.get('vector_diff', []))

            print(f"  🔧 補正対象: {item_id}")
            for i in unexpected_indices:
                diff = vector_diff[i]
                attenuation = diff * ALPHA # 減衰量を計算
                original_value = corrected_vector[i]
                corrected_value = max(0.0, original_value * (1 - attenuation))
                
                print(f"    - 次元 {i:<2}: 差分={diff:.4f}, 値を {original_value:.4f} -> {corrected_value:.4f} に補正")
                corrected_vector[i] = corrected_value
            
            # 辞書内のベクトルを更新
            db_dict[item_id]['meaning_vector'] = corrected_vector.tolist()
        else:
            print(f"  ⚠️ 警告: 失敗ログに記載のID '{item_id}' がデータベースに見つかりません。")

    # 3. 修正後のデータベースを新しいファイルに書き出す
    stabilized_db_data = list(db_dict.values())
    try:
        with open(STABILIZED_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(stabilized_db_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ データベースの安定化が完了しました。")
        print(f"   新しいデータベースが {STABILIZED_DB_PATH} に保存されました。")
    except IOError as e:
        print(f"\n❗ エラー: 安定化済みデータベースの書き込みに失敗しました: {e}")

if __name__ == "__main__":
    stabilize_database()

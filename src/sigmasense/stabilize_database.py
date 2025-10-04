import json
import os
import numpy as np
import argparse
import shutil

# 定数
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
config_dir = os.path.join(project_root, 'config')
log_dir = os.path.join(project_root, 'sigma_logs')

FAILURE_LOG_PATH = os.path.join(log_dir, "functor_consistency_failures.jsonl")
DEFAULT_SOURCE_DB_PATH = os.path.join(config_dir, "sigma_product_database_custom_ai_generated.json")
DEFAULT_STABILIZED_DB_PATH = os.path.join(config_dir, "sigma_product_database_stabilized.json")
ALPHA = 0.5 # 補正係数

def stabilize_database(source_db_path, stabilized_db_path):
    """失敗ログに基づいてデータベースを安定化させる"""
    print("🌿 差分補正によるデータベース安定化を開始します...")

    # 1. ソースとなるデータベースを読み込む
    try:
        with open(source_db_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    except FileNotFoundError:
        print(f"❗ エラー: ソースデータベースが見つかりません: {source_db_path}")
        return
    except json.JSONDecodeError:
        print(f"❗ エラー: ソースデータベースのJSON形式が不正です: {source_db_path}")
        return

    # 扱いやすいようにIDをキーにした辞書に変換
    db_dict = {item['id']: item for item in db_data}

    # 2. 失敗ログを読み込んで補正処理を行う
    try:
        with open(FAILURE_LOG_PATH, 'r', encoding='utf-8') as f:
            failure_logs = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"✅ 失敗ログファイルが見つかりません。補正は不要です。 ({FAILURE_LOG_PATH})")
        # ログがない場合は、ソースをそのまま安定版としてコピーする
        try:
            shutil.copyfile(source_db_path, stabilized_db_path)
            print(f"   ソースデータベースを {stabilized_db_path} にコピーしました。")
        except IOError as e:
            print(f"\n❗ エラー: データベースのコピーに失敗しました: {e}")
        return

    if not failure_logs:
        print("✅ 失敗ログはありませんでした。データベースは既に安定的です。")
        # ログがない場合は、ソースをそのまま安定版としてコピーする
        try:
            shutil.copyfile(source_db_path, stabilized_db_path)
            print(f"   ソースデータベースを {stabilized_db_path} にコピーしました。")
        except IOError as e:
            print(f"\n❗ エラー: データベースのコピーに失敗しました: {e}")
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
        with open(stabilized_db_path, 'w', encoding='utf-8') as f:
            json.dump(stabilized_db_data, f, indent=2, ensure_ascii=False)
        print("\n✅ データベースの安定化が完了しました。")
        print(f"   新しいデータベースが {stabilized_db_path} に保存されました。")
    except IOError as e:
        print(f"\n❗ エラー: 安定化済みデータベースの書き込みに失敗しました: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='失敗ログに基づいてデータベースを安定化させます。\n失敗ログがない場合は、ソースデータベースをそのまま安定化済みデータベースとしてコピーします。',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--source', type=str, default=DEFAULT_SOURCE_DB_PATH,
                        help=f'ソースデータベースのパス。\n(デフォルト: {DEFAULT_SOURCE_DB_PATH})')
    parser.add_argument('--output', type=str, default=DEFAULT_STABILIZED_DB_PATH,
                        help=f'安定化済みデータベースの出力パス。\n(デフォルト: {DEFAULT_STABILIZED_DB_PATH})')
    args = parser.parse_args()

    stabilize_database(args.source, args.output)

import json
import numpy as np
import argparse
import os
import sys

# スクリプトのディレクトリからプロジェクトのルートディレクトリを特定し、sys.pathに追加
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dimension_loader import DimensionLoader # 修正: クラスをインポート

# DimensionLoaderのインスタンスを生成
try:
    dimension_loader = DimensionLoader()
except Exception as e:
    print(f"❗ DimensionLoaderの初期化に失敗しました: {e}")
    sys.exit(1)

def diagnose_unrelated(log_entry):
    """
    "Unrelated"と分類された単一のログエントリを診断する。
    各意味軸（レイヤー）のエネルギー（ベクトルの大きさ）を計算し、
    エネルギーが低い軸を「情報不足」の候補として挙げる。
    """
    vector = np.array(log_entry.get('vector', []))
    if not vector.any():
        return ["ベクトルが空です。"]

    diagnoses = []
    
    # 各レイヤーのエネルギーを計算
    layer_energies = {}
    # dimension_loaderに直接アクセスする代わりに、定義済みのマップを使用
    for layer_name in dimension_loader._layer_map.keys():
        indices = dimension_loader.get_layer_indices(layer_name)
        if indices:
            layer_vector = vector[indices]
            # L2ノルムの2乗でエネルギーを計算
            energy = np.linalg.norm(layer_vector)**2
            layer_energies[layer_name] = energy

    # エネルギーが全体の平均に比べて著しく低いレイヤーを特定
    if not layer_energies:
        return ["レイヤー情報がありません。"]
        
    total_energy = sum(layer_energies.values())
    avg_energy = total_energy / len(layer_energies) if len(layer_energies) > 0 else 0

    for layer, energy in layer_energies.items():
        # 平均の10%以下のエネルギーしかないレイヤーを「情報不足」と見なす
        if avg_energy > 0 and energy < avg_energy * 0.1:
            diagnoses.append(f"'{layer.capitalize()}'軸の情報が不足している可能性があります (エネルギー: {energy:.4f})")

    if not diagnoses:
        diagnoses.append("明確な情報不足の軸は見つかりませんでした。全体的に情報が曖昧である可能性があります。")

    return diagnoses

def main(log_file):
    """
    ログファイルを読み込み、照合不能（Unrelated）な結果を診断する。
    """
    print(f"🩺 Nova Diagnoser: 照合不能群の診断を開始します。")
    print(f"   ログファイル: {log_file}")
    print("="*70)

    unrelated_count = 0
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    result = json.loads(line)
                    if result.get('response', {}).get('classification') == 'Unrelated':
                        unrelated_count += 1
                        image_path = result.get('image_path', f'ログ {i+1}')
                        print(f"❗診断対象: {image_path}")
                        
                        diagnoses = diagnose_unrelated(result)
                        for d in diagnoses:
                            print(f"  -> {d}")
                        print("-" * 50)

                except json.JSONDecodeError:
                    print(f"  ❗ line {i+1} のJSONパースに失敗しました。")
    except FileNotFoundError:
        print(f"❗エラー: ログファイルが見つかりません: {log_file}")
        return
    
    print("="*70)
    print(f"診断完了。{unrelated_count}件の照合不能な結果が見つかりました。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SigmaSenseのログファイルを分析し、照合不能な結果を診断します。')
    parser.add_argument('log_file', type=str, help='分析対象の.jsonlログファイル')
    args = parser.parse_args()
    
    main(args.log_file)
import json
import numpy as np
import argparse
import os
import sys
from collections import deque

# スクリプトのディレクトリからプロジェクトのルートディレクトリを特定し、sys.pathに追加
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.dimension_loader import DimensionLoader
from src.personal_memory_graph import PersonalMemoryGraph
from src.information_metrics import compute_self_correlation_score

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

def analyze_self_correlation_trends(memory_graph: PersonalMemoryGraph, window_size=10, deviation_threshold=2.0):
    """
    過去の自己相関スコアのトレンドを分析し、異常な変動を検出する。
    """
    print("\n--- 自己相関スコアのトレンド分析を開始します ---")
    all_memories = memory_graph.get_all_memories()
    if len(all_memories) < window_size + 1: # 履歴と現在のスコアを比較するため
        print("  十分な履歴データがありません。トレンド分析をスキップします。")
        return

    self_correlation_scores = deque(maxlen=window_size) # 最新のN個のスコアを保持
    anomalies = []

    for i, mem in enumerate(all_memories):
        score = mem.get("experience", {}).get("auxiliary_analysis", {}).get("self_correlation_score")
        if score is None:
            continue

        self_correlation_scores.append(score)

        if len(self_correlation_scores) == window_size:
            # 移動平均と移動標準偏差を計算
            current_window_scores = np.array(list(self_correlation_scores))
            mean_sc = np.mean(current_window_scores)
            std_sc = np.std(current_window_scores)

            # 現在のスコアが移動平均から大きく逸脱しているかチェック
            if std_sc > 0:
                z_score = abs((score - mean_sc) / std_sc)
                if z_score >= deviation_threshold:
                    anomalies.append(f"  ❗ 経験 {i+1} ({mem.get("experience", {}).get('source_image_name', "N/A')}): 自己相関スコアが異常 ({score:.2f}, 平均: {mean_sc:.2f}, 標準偏差: {std_sc:.2f})")
            elif score != mean_sc: # std_sc == 0だがスコアが異なる場合
                 anomalies.append(f"  ❗ 経験 {i+1} ({mem.get("experience", {}).get('source_image_name', "N/A')}): 自己相関スコアが異常 ({score:.2f}, 過去は常に {mean_sc:.2f})")

    if anomalies:
        print("--- 自己相関スコアの異常トレンドが検出されました ---")
        for anomaly in anomalies:
            print(anomaly)
    else:
        print("  自己相関スコアの異常トレンドは検出されませんでした。")
    print("--- トレンド分析を終了します ---")

def main():
    """
    ログファイルを読み込み、照合不能（Unrelated）な結果を診断し、
    自己相関スコアのトレンド分析を実行する。
    """
    parser = argparse.ArgumentParser(description='SigmaSenseのログファイルを分析し、照合不能な結果を診断します。')
    parser.add_argument('--log_file', type=str, default=os.path.join(project_root, "sigma_logs", "response_log.jsonl"),
                        help='分析対象の.jsonlログファイル (デフォルト: sigma_logs/response_log.jsonl)')
    parser.add_argument('--memory_path', type=str, default=os.path.join(project_root, "sigma_logs", "personal_memory.jsonl"),
                        help='PersonalMemoryGraphのパス (デフォルト: sigma_logs/personal_memory.jsonl)')
    parser.add_argument('--window_size', type=int, default=10,
                        help='自己相関スコアのトレンド分析に使用する移動平均のウィンドウサイズ (デフォルト: 10)')
    parser.add_argument('--deviation_threshold', type=float, default=2.0,
                        help='自己相関スコアの異常と見なす標準偏差の閾値 (デフォルト: 2.0)')
    args = parser.parse_args()

    print(f"🩺 Nova Diagnoser: 診断を開始します。")
    print(f"   ログファイル: {args.log_file}")
    print("="*70)

    unrelated_count = 0
    try:
        with open(args.log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    result = json.loads(line)
                    if result.get('ethics_passed') == False: # 倫理チェックで失敗したものを診断対象とする
                        unrelated_count += 1
                        image_path = result.get('source_image_name', f'ログ {i+1}')
                        print(f"❗診断対象 (倫理チェック失敗): {image_path}")
                        
                        # ここでdiagnose_unrelatedを呼び出すことも可能だが、
                        # Novaの役割拡張として、より高レベルな診断を行う
                        # 例: どの倫理モジュールが失敗したか、その理由など
                        ethics_log = result.get('ethics_log', [])
                        for entry in ethics_log:
                            if "Blocked" in entry or "Warning" in entry:
                                print(f"  -> {entry}")
                        print("-" * 50)

                except json.JSONDecodeError:
                    print(f"  ❗ line {i+1} のJSONパースに失敗しました。")
    except FileNotFoundError:
        print(f"❗エラー: ログファイルが見つかりません: {args.log_file}")
    
    print("="*70)
    print(f"診断完了。{unrelated_count}件の倫理チェック失敗が見つかりました。")

    # PersonalMemoryGraphをロードして自己相関スコアのトレンド分析を実行
    memory_graph = PersonalMemoryGraph(args.memory_path)
    analyze_self_correlation_trends(memory_graph, args.window_size, args.deviation_threshold)


if __name__ == '__main__':
    main()
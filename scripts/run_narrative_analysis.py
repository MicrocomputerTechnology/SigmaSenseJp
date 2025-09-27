import argparse
import os
import sys

# プロジェクトのルートをシステムパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.narrative_analyzer import NarrativeAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description='SigmaSenseの個人記憶ログを分析し、特定の主題に関する物語の系譜を追跡します。',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="実行例: python scripts/run_narrative_analysis.py --subject circle_center"
    )
    parser.add_argument(
        '--subject', 
        type=str, 
        default='circle_center',
        help='分析したい主題（画像のIDなど）。\n例: circle_center'
    )
    parser.add_argument(
        '--log_file', 
        type=str, 
        default='sigma_logs/personal_memory.jsonl',
        help='分析対象の.jsonlログファイルのパス。'
    )

    args = parser.parse_args()

    # スクリプトからの相対パスでlog_fileのパスを構築
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    log_path = os.path.join(project_root, args.log_file)

    if not os.path.exists(log_path):
        print(f"❗エラー: ログファイルが見つかりません: {log_path}")
        sys.exit(1)

    analyzer = NarrativeAnalyzer(log_path)
    analyzer.trace_narrative_for_image(args.subject)

if __name__ == '__main__':
    main()


## 7. GitHub Actionsワークフロー

本プロジェクトでは、開発プロセスを自動化し、コードの品質と一貫性を保つためにGitHub Actionsを活用しています。主要なワークフローは以下の通りです。

### `manual-workflows.yml`

- **目的**: プロジェクトの様々なスクリプトを手動で実行し、システム全体の統合的な動作を確認するためのワークフローです。モデルのダウンロード、データベースの構築、各種分析、シミュレーション、画像・ベクトル生成など、広範なタスクをカバーします。
- **トリガー**: `workflow_dispatch` (GitHub UIから手動で実行)
- **実行内容の概要**:
  - 依存関係のインストール
  - モデルのダウンロード
  - 意味ベクトルデータベースの構築
  - Ollamaのセットアップと検証
  - 各種スクリプトの実行 (`run_sigma.py`, `run_benchmark.py`, `run_learning_objective.py`, `run_sheaf_analysis.py`, `run_functor_check.py`, `stabilize_database.py`, `run_ethics_check_on_text.py`, `run_narrative_analysis.py`, `run_narrative_processing_experiment.py`, `run_offline_evolution_cycle.py`, `run_online_integration.py`, `run_reconstruction_experiment.py`, `generate_test_image.py`, `generate_number_image.py`, `generate_ai_image_vectors.py`, `generate_ai_dimensions.py`, `run_terrier_comparison.py`, `run_psyche_simulation.py` など)

### `test.yml`

- **目的**: プルリクエストが作成された際に自動的に実行され、コードの品質と機能が損なわれていないことを検証するための継続的インテグレーション (CI) ワークフローです。
- **トリガー**: `pull_request`
- **実行内容の概要**:
  - Python環境のセットアップ
  - 依存関係のインストール (`ginza`, `pytest` など)
  - `ginza` の機能チェック
  - モデルのダウンロードの検証
  - テスト用のダミーファイルの作成
  - `pytest` を用いたユニットテストおよび統合テストの実行
  - `scripts/run_benchmark.py` の実行による基本的な性能評価
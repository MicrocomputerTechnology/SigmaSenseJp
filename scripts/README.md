# 実行可能スクリプト

このディレクトリには、SigmaSenseシステムのさまざまな部分を実行するための各種スクリプトが含まれています。

## 主要な実行スクリプト

- **`run_sigma.py`**: 第十五次世代システムのメインの思考サイクル（`process_experience`）を実行します。
- **`run_learning_objective.py`**: 与えられた学習目標を処理するための自己拡張ワークフローを開始します。
- **`run_psyche_simulation.py`**: 豊川モデルに基づき、システムの心理状態のシミュレーションを実行します。

## 分析・評価スクリプト

- **`run_benchmark.py`**: `sigma_images`データセットを使用して、システムの基本的な分類性能を評価するためのベンチマークを実行します。
- **`run_functor_check.py`**: `tools/functor_consistency_checker.py`の機能をラップし、データベースの論理的一貫性（関手性）をチェックするユーティリティスクリプトだと思われます。
- **`run_sheaf_analysis.py`**: 画像内の局所的な特徴が、層理論の貼り合わせ条件を満たしているか（矛盾がないか）を検証します。
- **`run_ethics_check_on_text.py`**: 外部のテキスト入力に対して倫理チェックを実行します。
- **`run_narrative_analysis.py`**: 与えられた主題について、語りの分析を実行します。
- **`run_terrier_comparison.py`**: テリア犬種に関連する特定の比較タスクを実行します。

## データベース・モデル関連スクリプト

- **`build_knowledge_store.py`**: `PocketLibrary`に関連すると思われる知識ストアを構築します。
- **`download_models.py`**: プロジェクトに必要なすべての機械学習モデルをダウンロードします。
- **`migrate_personal_memory.py`**: 個人的な記憶データをあるフォーマットやスキーマから別のものへ移行します。

## 実験用スクリプト

- **`run_narrative_processing_experiment.py`**: 語り処理に関連する実験を実行します。
- **`run_offline_evolution_cycle.py`**: 「ヴェトラ」エージェントのためのオフライン進化サイクルを実行します。
- **`run_online_integration.py`**: オフラインでの学習成果が「オリエン」エージェントによってレビューされ、構造化されるオンライン統合プロセスを実行します。
- **`run_reconstruction_experiment.py`**: 意味ベクトルの再構成に関連する実験を実行します。

## ユーティリティスクリプト

- **`analyze_sentence.py`**: おそらく自然言語処理ツールを使用して、単一の文を分析します。
- **`run_gemini_connection_test.py`**: Gemini APIへの接続をテストします。
- **`run_unknown_word_test.py`**: おそらく`SymbolicReasoner`と`PocketLibrary`を使用して、未知の単語を処理するシステムの能力をテストします。
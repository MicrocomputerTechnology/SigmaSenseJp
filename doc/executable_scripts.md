## 付録D: 実行可能スクリプト一覧

プロジェクト内で直接実行されることを意図した主要なスクリプトの一覧です。

### メインプロセス
- **`scripts/run_sigma.py`**
  - 説明: 第十五次世代の統合思考サイクルを実行するメインスクリプト。
  - 実行例: `python scripts/run_sigma.py`

- **`scripts/run_learning_objective.py`**
  - 説明: 外部から与えられた学習目標を処理する自己拡張ワークフローを開始します。
  - 実行例: `python scripts/run_learning_objective.py --objective "新しい犬種を学習する"`

### データベースとモデル
- **`src/build_database.py`**
  - 説明: 画像ディレクトリから意味ベクトルデータベースを構築・更新します。
  - 実行例: `python src/build_database.py --img_dir sigma_images`

- **`scripts/download_models.py`**
  - 説明: プロジェクトに必要な機械学習モデルをすべてダウンロードします。
  - 実行例: `python scripts/download_models.py`

### 分析と評価
- **`scripts/run_benchmark.py`**
  - 説明: `sigma_images` データセットを使い、システムの基本的な分類性能を評価します。
  - 実行例: `python scripts/run_benchmark.py`

- **`tools/functor_consistency_checker.py`**
  - 説明: データベースの論理的一貫性（関手性）を診断し、問題点をログに出力します。
  - 実行例: `python tools/functor_consistency_checker.py`

- **`src/stabilize_database.py`**
  - 説明: `functor_consistency_checker.py` の診断結果に基づき、データベースを補正・安定化させます。
    - `--source`: 補正元のデータベースパスを指定します。
    - `--output`: 補正後のデータベース出力パスを指定します。
  - 実行例: `python src/stabilize_database.py --source config/source.json --output config/stabilized.json`

- **`scripts/run_sheaf_analysis.py`**
  - 説明: 画像内の局所的な特徴が、層理論の貼り合わせ条件を満たしているか（矛盾がないか）を検証します。
  - 実行例: `python scripts/run_sheaf_analysis.py --image_path sigma_images/multi_object.jpg`

- **`scripts/run_ethics_check_on_text.py`**
  - 説明: 入力されたテキストに対して倫理チェックを実行します。
  - 実行例: `python scripts/run_ethics_check_on_text.py --text "これはテスト用の安全なテキストです。"`
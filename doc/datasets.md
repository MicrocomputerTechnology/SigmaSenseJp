## 付録C：データセットの来歴と品質保証

本プロジェクトで利用されるデータ、特にAIによって生成されるデータの出所、生成プロセス、および品質保証の考え方を以下に示します。

### 1. 意味次元定義 (`vector_dimensions_*.json`)

意味次元の定義ファイルは、`src/generate_ai_dimensions.py` スクリプトによって生成されます。このスクリプトは、特定の要件を記述したプロンプトをGemini APIに送信し、その応答として次元定義のJSONを受け取ります。

-   **生成プロセス**:
    -   **`config/vector_dimensions_custom_ai.json`**: `generate_ai_dimensions.py` に内蔵された `prompt_selia` を使用し、幾何学的図形を分析するための次元を生成します。
    -   **`config/vector_dimensions_custom_ai_lyra.json`**: 同様に `prompt_lyra` を使用し、動物の「感性」的な特徴を捉えるための次元を生成します。
    -   **`config/vector_dimensions_custom_ai_terrier.json`**: `config/terrier_prompt.txt` をプロンプトとして使用し、テリア犬種を見分けるための専門的な次元を生成します。
-   **品質保証**:
    生成された各次元には `algorithm_idea` が含まれており、その計算方法が明確に定義されています。これにより、次元の意図と実装が一致していることを確認できます。

### 2. 意味ベクトルデータベース (`sigma_product_database_*.json`)

画像の意味ベクトルを格納したデータベースは、以下の2段階のプロセスを経て生成・検証されます。

-   **ステージ1: 生成 (`build_database.py`)**
    1.  `sigma_images/` ディレクトリ内の全ての画像が対象となります。
    2.  `DimensionGenerator`が、全種類の次元定義ファイル（`.json`, `.yaml`）を読み込みます。
    3.  各画像に対して、複数の画像分析エンジン（OpenCV, MobileNet, ResNet等）が特徴量を抽出し、それに基づいて統合された一つの「意味ベクトル」を生成します。
    4.  この結果が `config/sigma_product_database_custom_ai_generated.json` として保存されます。
    5.  **Note**: このビルドプロセス中に `sigma_logs/functor_consistency_failures.jsonl` が存在する場合、`CorrectionApplicator`によって自動的にベクトル補正が適用されます。

-   **ステージ2: 安定化 (`stabilize_database.py`)**
    1.  **品質検証**: `tools/functor_consistency_checker.py` を実行し、データベース内のベクトルの一貫性を検証します。このツールは、画像を回転させたり色を変えたりといった変換を加え、その際にベクトルの次元が予期せぬ影響を受けていないか（関手性）をチェックします。
    2.  **ログ生成**: 一貫性に問題が見つかった場合、その詳細が `sigma_logs/functor_consistency_failures.jsonl` に記録されます。
    3.  **補正実行**: `stabilize_database.py` スクリプトがこのログファイルを読み込み、問題のあったベクトルの次元値を補正（減衰）します。
    4.  **保存**: 補正後のクリーンなデータベースが `config/sigma_product_database_stabilized.json` として保存されます。

この「生成 → 検証 → 補正」のサイクルが、データベースの品質と信頼性を保証する中心的なメカニズムです。

### 3. サードパーティ製データとライセンス

本プロジェクトが利用する主要なサードパーティ製データと、そのライセンスは以下の通りです。

-   **Haar Cascade分類器 (`config/haarcascade_dog_face.xml`)**:
    -   **出所**: OpenCVライブラリ
    -   **ライセンス**: Apache 2.0 License
-   **機械学習モデル (`models/`)**:
    -   **対象**: MobileNetV1, ResNetV2, MobileViT, EfficientNet-Lite 等
    -   **出所**: 主にTensorFlow Hubで公開されている学習済みモデル
    -   **ライセンス**: Apache 2.0 License

プロジェクトの成果物は、これらのライセンス条件を尊重する必要があります。
### 1.1.2. 定量的評価

本プロジェクトの性能は、以下のタスクと指標によって定量的に評価されます。

- **タスク例**:
  - **幾何学図形の識別**: `sigma_images` 内の基本的な図形（円、四角形など）を正しく識別できるか。`scripts/run_benchmark.py` を用いて評価。
  - **犬種の分類**: `config/terrier_prompt.txt` で定義された特徴を用いて、ノーフォークテリアとケアーンテリアの画像を分類できるか。
  - **論理的一貫性の維持**: `tools/functor_consistency_checker.py` を実行し、意図しない副作用なしにデータベースが安定しているか。

- **評価指標**:
  - **分類精度 (Accuracy)**: 
    - **幾何学図形識別タスク**: **76.92%** (10/13)
      - `scripts/run_benchmark.py` による `sigma_images` データセットでの評価結果 (2025/09/26時点)。
      - 詳細は `scripts/run_benchmark.py` の実行ログ、および `tests/test_benchmark_classification.py` を参照。
    - 上記の分類タスクにおいて、正しく分類された画像の割合。
    ```
    Accuracy = (True Positives + True Negatives) / Total Samples
    ```
  - **関手性一貫性率 (Functorial Consistency Rate)**:
    `functor_consistency_checker.py` のテストにおいて、副作用（予期せぬ次元の変化）が発生しなかったテストケースの割合。
    ```
    Consistency Rate = 1 - (Number of Failed Cases / Total Test Cases)
    ```
  - **情報量基準**: KLダイバージェンスやワッサースタイン距離を用いて、2つの意味ベクトルの分布間の「距離」を測定し、照合の確信度とします。

## 4. ベンチマークの実行

プロジェクトの基本的な分類性能を評価するためのベンチマークを実行できます。

```bash
python scripts/run_benchmark.py
```

このスクリプトは `sigma_images` データセットを使用し、幾何学図形の分類精度を測定します。実行後、コンソールに正解率と各画像の分類結果が表示されます。
また、`tests/test_benchmark_classification.py` には、個別の画像に対する期待される挙動を定義したユニットテストが含まれており、`pytest` を実行することでも検証が可能です。
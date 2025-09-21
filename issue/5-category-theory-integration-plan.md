# Issue #5: 圏論統合の高レベル設計案

## 1. 目標

SigmaSense内部で圏論的特性を明示的に表現し、検証することで、暗黙の仮定を超え、数学的に厳密なフレームワークを構築する。これにより、システムの論理的一貫性、予測可能性、変換に関する推論能力を向上させる。

## 2. 主要概念のマッピング

### 2.1. 圏 (Categories)

*   **`ImageCategory`**: オブジェクトは画像（または画像パス/データ）。射（Morphisms）は画像変換（例：回転、スケール、平行移動、色変更）。
*   **`VectorSpaceCategory`**: オブジェクトは意味ベクトル（NumPy配列）。射は線形変換またはその他のベクトル空間操作。
*   **`MeaningCategory`**: オブジェクトは抽象的な「意味」や「概念」（例：「犬」、「四角」、「赤」）。射は論理的推論や関係性（例：「is-a」、「原因」）。これは`WorldModel`にマッピングされる。

### 2.2. 関手 (Functors)

*   **`PerceptionFunctor (F_P)`**: `ImageCategory`から`VectorSpaceCategory`への写像。
    *   **オブジェクト:** `F_P(画像) = 意味ベクトル`（`DimensionGenerator.generate_dimensions`経由）。
    *   **射:** `F_P(画像変換関数)`は、対応する`ベクトル変換関数`に対応するべきである。これは`SigmaFunctor.check_functoriality`が現在テストしている内容である。`ベクトル変換関数`の生成を形式化する必要がある。
*   **`ReasoningFunctor (F_R)`**: `VectorSpaceCategory`から`MeaningCategory`への写像。
    *   **オブジェクト:** `F_R(意味ベクトル) = 論理的事実`（`SymbolicReasoner`、`LogicalPattern_Suggester`経由）。
    *   **射:** `VectorSpaceCategory`における変換（例：ベクトル成分の変更）は、`MeaningCategory`における論理的推論に対応するべきである。

### 2.3. 自然変換 (Natural Transformations)

*   これらは異なる関手間の関係性を表す。例えば、2つの異なる画像特徴量抽出エンジン（`OpenCVEngine`、`EfficientNetEngine`）が両方とも`PerceptionFunctor`として機能する場合、自然変換は、これらの2つの関手が画像変換に関して「自然に」振る舞うこと（つまり、画像を回転させてからOpenCVで特徴量を抽出することと、画像を回転させてからEfficientNetで特徴量を抽出することが「自然に同等」であること）を検証できる。これは実装が非常に高度な概念である。

## 3. アーキテクチャ上の含意と次のステップ

### 3.1. 射の形式化

*   **画像変換:** `group_theory_action.py`を拡張し、`PIL.Image`オブジェクトに適用できる、より包括的な画像変換関数セットを提供する。
*   **ベクトル変換:** 意味ベクトルに対する変換を定義するモジュール（例：`src/vector_transforms.py`）を開発する。これらは理想的には画像変換に対応するべきである。例えば、「色相回転」画像変換には、対応する「色相次元シフト」ベクトル変換があるべきである。

### 3.2. `SigmaFunctor`の強化

*   既存の`SigmaFunctor.check_functoriality`は良い出発点である。様々な`image_transform_func`とそれに対応する`vector_transform_func`のペアを体系的にテストするように拡張する必要がある。
*   これらの（画像変換、ベクトル変換）ペアとその期待される関係性を明示的に格納する`FunctorialMap`クラスの追加を検討する。

### 3.3. `MeaningCategory` (WorldModel)の統合

*   `WorldModel`における論理的推論と関係性を`MeaningCategory`における射としてどのように見なせるかを探る。
*   異なる推論プロセス（例：`SymbolicReasoner` vs. ニューラル推論モジュール）間の「自然変換」を定義できるか？

### 3.4. 明確化のためのリファクタリング

*   形式化を進めるにつれて、既存のモジュールの一部は、その「関手的」な性質を明示的に公開するためにリファクタリングが必要になる可能性がある。

## 4. 当面の次の行動 (実装のため)

最も具体的な次のステップは、**画像変換とベクトル変換の関係性を形式化すること**である。これは、以下のことを意味する。

*   **画像変換に対応するように設計されたベクトル変換のためのモジュールを実装する。**
*   **これらの対応関係をより厳密にテストするために`SigmaFunctor`を拡張する。**

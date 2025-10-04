# Phase 4.2: 論理推論エンジンの実装 (Logic Reasoning Engine Implementation) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **既存ファイル修正:** `src/hoho/symbolic_reasoner.py`
  - PLN相当の形式論理推論エンジンとして拡張。
- **既存ファイル修正:** `src/sigmasense/world_model.py`
  - 知識のハイパーグラフ構造と真実値（確信度、信頼度）をサポートするスキーマ拡張。
- **新規ファイル:** `src/hoho/truth_value_propagator.py` (仮)
  - 真実値伝播のルールを実装し、知識の確信度を更新する。
- **新規ファイル:** `src/hoho/contradiction_detector.py` (仮)
  - 知識の矛盾を検出し、矛盾解消戦略を提供する。

## 3. クラス/関数設計 (Class/Function Design)
### `src/hoho/symbolic_reasoner.py`
- **クラス:** `SymbolicReasoner`
  - **修正:** `__init__(self, world_model: WorldModel, truth_value_propagator: TruthValuePropagator, contradiction_detector: ContradictionDetector)`
    - `TruthValuePropagator`と`ContradictionDetector`のインスタンスを受け取るように変更。
  - **修正:** `reason(self, context: dict) -> dict`
    - 入力コンテキストと`WorldModel`の知識に基づき、確信度付きの推論結果を生成する。
    - 推論の過程で`TruthValuePropagator`を利用し、確信度を伝播させる。
    - 新しい知識が生成された場合、`ContradictionDetector`で矛盾をチェックする。
  - **新規メソッド:** `add_knowledge(self, knowledge_statement: dict, confidence: float)`
    - 新しい知識を`WorldModel`に追加し、`TruthValuePropagator`で確信度を伝播させ、`ContradictionDetector`で矛盾をチェックする。
  - **新規メソッド:** `resolve_contradiction(self, contradiction_report: dict) -> bool`
    - 矛盾解消戦略を実行するインターフェース。

### `src/sigmasense/world_model.py`
- **クラス:** `WorldModel`
  - **修正:** 知識表現のスキーマを拡張し、各ノードとエッジに真実値（確信度、信頼度）を格納できるようにする。
  - **新規メソッド:** `update_truth_value(self, node_id: str = None, edge_id: str = None, new_confidence: float)`
    - 特定のノードまたはエッジの真実値を更新する。
  - **新規メソッド:** `get_knowledge_with_truth_value(self, query: dict) -> list[dict]`
    - 真実値情報を含めて知識を取得する。

### `src/hoho/truth_value_propagator.py`
- **クラス:** `TruthValuePropagator`
  - **メソッド:** `__init__(self, world_model: WorldModel)`
    - `WorldModel`のインスタンスを受け取る。
  - **メソッド:** `propagate(self, changed_knowledge_id: str, initial_confidence: float)`
    - 変更された知識から開始し、定義されたルールに基づいて関連する知識の真実値を伝播・更新する。
  - **メソッド:** `define_propagation_rules(self, rules: list[dict])`
    - 真実値伝播のルール（例: `AND`結合、`OR`結合、否定のルール）を定義する。

### `src/hoho/contradiction_detector.py`
- **クラス:** `ContradictionDetector`
  - **メソッド:** `__init__(self, world_model: WorldModel)`
    - `WorldModel`のインスタンスを受け取る。
  - **メソッド:** `detect(self, new_knowledge: dict) -> dict | None`
    - 新しい知識が既存の知識ベースと矛盾するかどうかを検出し、矛盾があればその詳細を報告する。
  - **メソッド:** `suggest_resolution(self, contradiction_report: dict) -> list[dict]`
    - 検出された矛盾に対して、可能な解消戦略（例: 確信度の低い方を修正、両方を不確実としてマーク）を提案する。

## 4. データフロー (Data Flow)
- `SymbolicReasoner`が外部からのクエリや新しい知識を受け取る。
- 新しい知識は`WorldModel`に追加され、`TruthValuePropagator`によって関連知識の真実値が更新される。
- `ContradictionDetector`は、新しい知識や真実値の更新によって生じる矛盾を監視・検出する。
- 矛盾が検出された場合、`SymbolicReasoner`は`ContradictionDetector`からの報告を受け、矛盾解消戦略を実行する。
- `SymbolicReasoner`は、確信度付きの知識を用いて推論結果を生成し、他のモジュールに提供する。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `SymbolicReasoner`: `TruthValuePropagator`と`ContradictionDetector`をDIで受け取るように変更。
- `WorldModel`: 真実値の格納と更新、取得のためのAPIを追加。
- `CausalDiscovery` (#278): 発見した因果関係ルールに確信度を付与し、`SymbolicReasoner.add_knowledge()`を通じて`WorldModel`に登録する。

## 6. テスト計画 (Test Plan)
- `TruthValuePropagator`の単体テスト: 定義されたルールに基づいて真実値が正しく伝播することを確認する。
- `ContradictionDetector`の単体テスト: 既知の矛盾パターンを正しく検出し、解消戦略を提案できることを確認する。
- `SymbolicReasoner`の統合テスト: 確信度付きの知識を用いた推論、新しい知識の追加、矛盾検出・解消の一連のプロセスが正しく機能することを確認する。
- パフォーマンスベンチマーク: 大規模な知識グラフにおける真実値伝播と矛盾検出の計算コストを測定する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- 真実値の表現形式（例: 確率、ファジィ論理、区間）。
- 矛盾解消戦略の自動化レベルと、人間の介入の必要性。
- 計算複雑性への対処（例: 近似推論、サンプリング）。
- 形式論理エンジンへの生物的・歴史的法則の組み込み方法の具体化。

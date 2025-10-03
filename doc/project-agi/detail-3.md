# Phase 3: 理論モデルの構築 (Theoretical Model Construction) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `src/theory/collective_intelligence_model.py` (仮)
  - 集合知の数理モデルとアトラクター概念の定式化を実装する。
- **新規ファイル:** `src/theory/attractor_dynamics.py` (仮)
  - アトラクターの検出、モデリング、安定性分析に関する具体的なアルゴリズムを実装する。
- **既存ファイル修正:** `src/hoho/symbolic_reasoner.py`
  - 形式論理エンジンを拡張し、生物的・歴史的法則を記述・推論可能にする。
- **既存ファイル修正:** `src/sigmasense/world_model.py`
  - 集合知モデルやアトラクターの概念を反映した知識表現の拡張。
- **既存ファイル修正:** `src/selia/personal_memory_graph.py`
  - 記憶のアトラクター形成をサポートするためのデータ構造の拡張。

## 3. クラス/関数設計 (Class/Function Design)
### `src/theory/collective_intelligence_model.py`
- **クラス:** `CollectiveIntelligenceModel`
  - **メソッド:** `__init__(self, world_model: WorldModel, pmg: PersonalMemoryGraph)`
    - `WorldModel`と`PersonalMemoryGraph`のインスタンスを受け取る。
  - **メソッド:** `formulate_model(self, data_sources: list) -> dict`
    - 生物学的、人類史的、情報圏のデータを統合し、集合知の数理モデルを定式化する。
    - 圏論、層理論、非線形力学系、情報幾何学などの概念を抽象化して表現する。
  - **メソッド:** `analyze_attractors(self, cognitive_state_data: dict) -> list[Attractor]`
    - システムの認知状態データからアトラクターを検出し、その特性（強度、安定性、収束速度）を分析する。
    - `AttractorDynamics`モジュールを利用する。

### `src/theory/attractor_dynamics.py`
- **クラス:** `AttractorDynamics`
  - **メソッド:** `detect_attractor(self, state_series: list) -> Attractor`
    - 時系列データからアトラクターを検出するアルゴリズム（例: リャプノフ指数、位相空間再構成）。
  - **メソッド:** `model_attractor(self, attractor_data: dict) -> AttractorModel`
    - 検出されたアトラクターを数理モデルとして表現する。
  - **メソッド:** `analyze_stability(self, attractor_model: AttractorModel) -> float`
    - アトラクターの安定性を評価する。

### `src/hoho/symbolic_reasoner.py`
- **クラス:** `SymbolicReasoner`
  - **修正:** `reason(self, context: dict) -> dict`
    - 形式論理エンジンを拡張し、生物的・歴史的な法則（進化論、エネルギー最適化など）を表現する新しい述語やルールを処理できるようにする。
    - `CollectiveIntelligenceModel`から提供される数理モデルの知見を推論に組み込む。

### `src/sigmasense/world_model.py`
- **クラス:** `WorldModel`
  - **修正:** 知識表現のスキーマを拡張し、集合知モデルやアトラクターの概念（例: 安定状態の定義、収束パス）を格納できるようにする。
  - **新規メソッド:** `get_attractor_data(self, query: dict) -> dict`
    - アトラクター関連のデータを取得する。

### `src/selia/personal_memory_graph.py`
- **クラス:** `PersonalMemoryGraph`
  - **修正:** 経験ログの構造に、アトラクター形成をサポートするためのメタデータ（例: 認知状態の時系列データ、行動パターンの履歴）を記録できるフィールドを追加する。

## 4. データフロー (Data Flow)
- `WorldModel`と`PersonalMemoryGraph`から提供される知識と経験データが`CollectiveIntelligenceModel`に渡される。
- `CollectiveIntelligenceModel`はこれらのデータを用いて集合知の数理モデルを定式化し、`AttractorDynamics`を利用してアトラクターを分析する。
- `SymbolicReasoner`は、`CollectiveIntelligenceModel`から得られた知見を基に、形式論理推論を拡張する。
- `WorldModel`と`PersonalMemoryGraph`は、集合知モデルやアトラクターの概念を反映した知識と経験を格納する。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `SymbolicReasoner`: `CollectiveIntelligenceModel`の知見を利用するように拡張。
- `WorldModel` & `PersonalMemoryGraph`: 集合知モデルとアトラクターの概念をサポートするデータスキーマの変更。
- `sigma_sense`のメインループ: `CollectiveIntelligenceModel`を初期化し、定期的にアトラクター分析を実行する。

## 6. テスト計画 (Test Plan)
- `CollectiveIntelligenceModel`が、与えられたデータから集合知の数理モデルを正しく定式化できることを確認する単体テスト。
- `AttractorDynamics`が、時系列データからアトラクターを検出し、その特性を分析できることを確認する単体テスト。
- `SymbolicReasoner`が、拡張された形式論理で生物的・歴史的法則を推論できることを確認する統合テスト。
- `WorldModel`と`PersonalMemoryGraph`が、新しいスキーマでアトラクター関連データを正しく格納・取得できることを確認する。
- シミュレーション環境で、システムがアトラクターへと収束する振る舞いを検証する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- 圏論、層理論などの高度な数学的概念を、Pythonコードでどのように効率的かつ正確に表現するか。
- アトラクターの検出とモデリングにおける計算コストとリアルタイム性のバランス。
- 形式論理エンジンへの生物的・歴史的法則の組み込み方法（述語論理、テンソル論理など）。
- 理論モデルの検証のためのシミュレーション環境の設計。

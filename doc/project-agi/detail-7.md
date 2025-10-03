# Phase 7: 認知リソースの最適化 (Cognitive Resource Optimization) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `src/metacontrol/time_constrained_reasoner.py` (仮)
  - NARSの思想に基づき、時間制約下での推論モデルを実装する。
- **新規ファイル:** `src/metacontrol/resource_allocator.py` (仮)
  - アトラクター理論に基づき、計算リソースを動的に配分する。
- **既存ファイル修正:** `src/hoho/symbolic_reasoner.py`
  - `TimeConstrainedReasoner`と連携し、推論の深さや広さを調整する。
- **既存ファイル修正:** `src/sigmasense/world_model.py`
  - 不確実性の内包をサポートする知識表現の拡張。
- **既存ファイル修正:** `src/planning/planner.py` (Phase 4.4で新規作成)
  - 時間的リミットを統合し、計画立案自体も時間制約を受けるようにする。
- **既存ファイル修正:** `src/theory/attractor_dynamics.py` (Phase 3で新規作成)
  - システムの認知状態からアトラクターをリアルタイムで検出し、リソース配分に活用する。

## 3. クラス/関数設計 (Class/Function Design)
### `src/metacontrol/time_constrained_reasoner.py`
- **クラス:** `TimeConstrainedReasoner`
  - **メソッド:** `__init__(self, symbolic_reasoner: SymbolicReasoner, planner: Planner)`
    - `SymbolicReasoner`と`Planner`のインスタンスを受け取る。
  - **メソッド:** `reason_with_time_limit(self, context: dict, time_limit_ms: int) -> dict`
    - 指定された時間制限内で、`SymbolicReasoner`を用いて可能な最善の推論結果を返す。
    - 時間に応じて推論の深さや広さを動的に調整する。
  - **メソッド:** `plan_with_time_limit(self, goal: dict, current_state: dict, time_limit_ms: int) -> list[dict]`
    - 指定された時間制限内で、`Planner`を用いて可能な最善の行動計画を生成する。

### `src/metacontrol/resource_allocator.py`
- **クラス:** `ResourceAllocator`
  - **メソッド:** `__init__(self, attractor_dynamics: AttractorDynamics, task_monitor: TaskMonitor)`
    - `AttractorDynamics`と`TaskMonitor`（新規モジュール、システム内の各タスクの状態を監視）のインスタンスを受け取る。
  - **メソッド:** `allocate_resources(self, current_task_states: dict) -> dict`
    - システム内の各タスクの状態（重要度、緊急度、進捗度）を監視し、`AttractorDynamics`から得られる知見に基づいて計算リソース（CPU、メモリ、時間）を動的に配分する。
    - 重要なタスクや収束しつつある認知状態（アトラクター）に多くのリソースを割り当てる。

### `src/hoho/symbolic_reasoner.py`
- **クラス:** `SymbolicReasoner`
  - **修正:** `reason(self, context: dict, time_limit_ms: int = None) -> dict`
    - `TimeConstrainedReasoner`からの指示に基づいて、時間制約を考慮した推論を実行できるようにする。
  - **修正:** 知識に時間とともに変化する確信度モデルを導入し、不確実性を効率的に管理する。

### `src/sigmasense/world_model.py`
- **クラス:** `WorldModel`
  - **修正:** 知識表現のスキーマを拡張し、不確実性（確信度の時間的変化）を格納できるようにする。

### `src/planning/planner.py` (Phase 4.4で新規作成)
- **クラス:** `Planner`
  - **修正:** `generate_plan(self, goal: dict, current_state: dict, time_limit_ms: int = None) -> list[dict]`
    - `TimeConstrainedReasoner`からの指示に基づいて、時間制約を考慮した計画立案を実行できるようにする。

### `src/theory/attractor_dynamics.py` (Phase 3で新規作成)
- **クラス:** `AttractorDynamics`
  - **修正:** `detect_attractor(self, state_series: list) -> Attractor`
    - システムの認知状態からアトラクターをリアルタイムで検出し、`ResourceAllocator`に情報を提供する。

## 4. データフロー (Data Flow)
- `ResourceAllocator`が`TaskMonitor`からシステム内の各タスクの状態を取得し、`AttractorDynamics`からアトラクター関連の知見を得る。
- `ResourceAllocator`はこれらの情報に基づいて、`TimeConstrainedReasoner`に各推論・計画プロセスに割り当てる時間リミットを指示する。
- `TimeConstrainedReasoner`は、`SymbolicReasoner`や`Planner`を呼び出す際にこの時間リミットを適用し、最適な推論・計画を生成する。
- `WorldModel`は、不確実性を含む知識を管理し、`SymbolicReasoner`に提供する。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `SymbolicReasoner`: `TimeConstrainedReasoner`からの時間制約付き推論要求を受け入れるように拡張。
- `Planner` (#153): `TimeConstrainedReasoner`からの時間制約付き計画立案要求を受け入れるように拡張。
- `WorldModel`: 不確実性を含む知識表現をサポートするように拡張。
- `AttractorDynamics` (#269, Phase 3): `ResourceAllocator`にアトラクター関連の知見を提供する。

## 6. テスト計画 (Test Plan)
- `TimeConstrainedReasoner`の単体テスト: 異なる時間制限下で、推論の深さや広さが適切に調整されることを確認する。
- `ResourceAllocator`の単体テスト: タスクの状態とアトラクター理論に基づいて、リソースが適切に配分されることを確認する。
- 統合テスト: シミュレーション環境で、システム全体が限られたリソース下でも、状況に応じて最適な推論と行動を選択できることを検証する。
- パフォーマンスベンチマーク: 時間制約下での推論と計画立案の応答速度と、リソース配分の効率を測定する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- トレードオフの最適化戦略: 厳密性と応答速度、あるいはリソース配分の最適なバランスを決定するメタ学習アルゴリズム。
- アトラクターのリアルタイム検出と、それに基づくリソース配分の動的な調整。
- 人間からの介入（例: 緊急事態発生時のリソース優先順位の変更）のメカニズム。
- 不確実性の表現と管理: 知識の確信度だけでなく、推論プロセスの不確実性も考慮に入れる。

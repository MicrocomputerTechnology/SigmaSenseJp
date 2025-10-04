# Phase 2.3: 物語性の強化 (Narrative Enhancement) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **既存ファイル修正:** `src/nova/meta_narrator.py`
  - ナラティブエンジンとして拡張。
- **既存ファイル修正:** `src/hoho/symbolic_reasoner.py`
  - 文学的モチーフとの類推機能を追加。
- **既存ファイル修正:** `src/selia/personal_memory_graph.py` (MetaNarratorが利用)
  - 物語生成に必要な経験ログの構造化を強化。
- **既存ファイル修正:** `src/hoho/pocket_library/` 関連ファイル (SymbolicReasonerが利用)
  - 文学的データの統合をサポート。

## 3. クラス/関数設計 (Class/Function Design)
### `src/nova/meta_narrator.py`
- **クラス:** `MetaNarrator`
  - **修正:** `__init__(self, config: dict = None, symbolic_reasoner: SymbolicReasoner = None)`
    - `SymbolicReasoner`のインスタンスを受け取るように変更し、文学的モチーフとの類推機能を利用可能にする。
  - **新規/修正:** `narrative_templates`
    - 歴史や文学の構造（例：英雄の旅、序破急、悲劇、喜劇）を表現するテンプレートを追加・拡張する。
    - テンプレートは、Issue #274で言及された「忠臣蔵、源氏物語、シェイクスピア、『鬼平犯科帳』、『史記』」などのモチーフを組み込めるように設計する。
  - **修正:** `narrate_growth(self, memory_graph: PersonalMemoryGraph) -> str`
    - 経験ログを分析する際に、`SymbolicReasoner`の類推機能を利用し、特定の経験がどの文学的モチーフに合致するかを判断する。
    - 判断結果に基づき、適切な物語テンプレートを選択し、より深みのある「成長の物語」を生成する。
  - **新規メソッド:** `narrate_event(self, event_context: dict) -> str`
    - 特定のイベント（例：パーティ内の葛藤、新たなスキル獲得）に対して、その場で短い「人情劇」や「英雄譚」を生成する。
    - ミルドの役割（日々の出来事を語る）をサポートする。

### `src/hoho/symbolic_reasoner.py`
- **クラス:** `SymbolicReasoner`
  - **新規メソッド:** `analogize_with_literary_motif(self, context: dict) -> list[dict]`
    - 与えられたコンテキスト（例：エージェントの行動、心理状態、環境）を分析し、知識グラフに統合された文学的データ（登場人物、関係性、プロット）と類推を行う。
    - 類推結果として、合致する文学的モチーフ（例: `{"motif": "忠臣蔵の義理", "similarity": 0.85}`）のリストを返す。
    - `PocketLibrary` (#155) から文学的データを参照する。

### `src/selia/personal_memory_graph.py`
- **クラス:** `PersonalMemoryGraph`
  - **修正:** 経験ログの構造に、物語生成に必要なメタデータ（例：感情の起伏、葛藤の有無、解決策の種類）を記録できるフィールドを追加する。

### `src/hoho/pocket_library/` 関連ファイル
- **修正:** 文学的データ（主要な文学作品や歴史的事件の登場人物、関係性、プロット）を構造化データとして格納・検索できる機能を追加する。
  - 具体的には、`DictionaryService`または`UnifiedDictionaryService` (#265) を拡張し、文学的エンティティとその属性を管理する。

## 4. データフロー (Data Flow)
- `PersonalMemoryGraph`に記録されたエージェントの経験ログが`MetaNarrator`に渡される。
- `MetaNarrator`は、必要に応じて`SymbolicReasoner`の`analogize_with_literary_motif`メソッドを呼び出し、経験を文学的モチーフと照合する。
- `SymbolicReasoner`は、`PocketLibrary`から文学的データを参照し、類推結果を`MetaNarrator`に返す。
- `MetaNarrator`は、これらの情報と内部の`narrative_templates`を用いて、共感を呼ぶ「物語」を生成する。
- 生成された物語は、外部への発信やエージェント自身の内省に利用される。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `MetaNarrator`: `SymbolicReasoner`のインスタンスをDI（Dependency Injection）で受け取るように変更。
- `SymbolicReasoner`: `PocketLibrary`の文学的データ検索機能を利用するように拡張。
- `PersonalMemoryGraph`: 経験ログのスキーマを拡張。
- `PocketLibrary`関連: 文学的データの格納・検索APIを追加。

## 6. テスト計画 (Test Plan)
- `SymbolicReasoner.analogize_with_literary_motif()`が、与えられたコンテキストに対して適切な文学的モチーフを類推できることを確認する単体テストを作成する。
- `MetaNarrator.narrate_growth()`が、経験ログと文学的モチーフの類推結果に基づいて、多様で陳腐でない物語を生成できることを確認する統合テストを作成する。
- ミルドとオリエンの役割に応じた物語生成（人情劇、英雄譚）が正しく機能することを確認する。
- 生成された物語の品質を評価するための定性的な評価基準を設ける。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- 文学的モチーフの知識表現形式（オントロジー、スキーマ）の設計。
- 物語生成における「事実と創作のバランス」をどのように制御するか。
- 文化的コンテキストの偏りを避けるための、多様な文学的データの収集と統合戦略。
- 生成された物語の外部発信チャネル（SNS連携、レポート生成など）の検討。

# Phase 2.2: 倫理的透明性の確保 (Ensuring Ethical Transparency) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `ETHICS.md`
  - `/doc` ディレクトリに配置。
  - Aegisが準拠する倫理原則を明文化する。
- **既存ファイル修正:** `src/aegis/aegis_ethics_filter.py`
  - 倫理的判断のロギング機能を追加。
  - `explain_decision` メソッドを追加。
- **新規ファイル:** `src/aegis/aegis_log_manager.py` (仮)
  - 倫理判断ログの管理（書き込み、読み込み、検索）を担当するモジュール。

## 3. クラス/関数設計 (Class/Function Design)
### `ETHICS.md`
- Markdown形式で、以下の内容を記述する。
  - Aegisの倫理フレームワークの概要
  - 各倫理原則の定義とID（例: `ETHIC_ID_001: 人類への危害禁止`）
  - 各原則の適用範囲と優先順位

### `src/aegis/aegis_ethics_filter.py`
- **クラス:** `AegisEthicsFilter`
  - **修正:** `__init__(self, profile_path: str, log_manager: AegisLogManager)`
    - `AegisLogManager`のインスタンスを受け取るように変更。
  - **修正:** `filter(self, narrative: str, image_name: str, context: dict) -> tuple[str, bool]`
    - `context`引数を追加し、判断に必要な追加情報（例: ユーザーID, 状況）を受け取る。
    - フィルタリングロジックの各ステップで、どの倫理ルールが適用されたか、その結果どうなったかを`AegisLogManager`に渡してログを生成する。
    - ログには、`[タイムスタンプ, 判断対象のコンテキスト, 適用された倫理ルールID, 判断結果(許可/ブロック), 判断理由の自然言語記述]`を含める。
  - **新規メソッド:** `explain_decision(self, context: dict) -> dict`
    - 特定のコンテキストが与えられた場合に、`filter`メソッドがどのような判断を下すか、そしてその根拠となる倫理原則を返す。
    - 内部的に`filter`メソッドのロジックをシミュレートし、判断に至るまでのステップと適用されたルールを詳細に記述する。

### `src/aegis/aegis_log_manager.py`
- **クラス:** `AegisLogManager`
  - **メソッド:** `__init__(self, log_file_path: str)`
    - ログファイルのパスを受け取る。
  - **メソッド:** `write_log(self, log_entry: dict)`
    - 構造化されたログエントリを `aegis_log.jsonl` に追記する。
    - パフォーマンスを考慮し、非同期書き込みやバッファリングを検討する。
  - **メソッド:** `get_logs(self, query: dict) -> list[dict]`
    - ログを検索する機能。

## 4. データフロー (Data Flow)
- 外部からの入力（語り、画像名、コンテキスト）が`AegisEthicsFilter.filter()`に渡される。
- `filter()`メソッド内で倫理的判断が下される過程で、`AegisLogManager.write_log()`を通じて詳細な判断ログが`aegis_log.jsonl`に記録される。
- 開発者や監査者は、`AegisEthicsFilter.explain_decision()`メソッドや`AegisLogManager.get_logs()`を通じて、倫理的判断の根拠や履歴を追跡・分析できる。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `aegis_ethics_filter.py`: `__init__`メソッドで`AegisLogManager`のインスタンスを受け取るように変更。`filter`メソッド内で`AegisLogManager`を呼び出す。
- `aegis_ethics_filter.py`を呼び出す上位モジュール（例: `MetaNarrator`や`sigma_sense`の出力部分）は、`filter`メソッドに`context`引数を渡すように変更が必要。

## 6. テスト計画 (Test Plan)
- `ETHICS.md` が作成され、倫理原則が明文化されていることを確認する。
- `AegisLogManager`の単体テスト: ログの書き込み、読み込み、検索が正しく機能することを確認する。
- `AegisEthicsFilter`の単体テスト:
  - `filter`メソッドが、ログを正しく生成し、`AegisLogManager`に渡すことを確認する。
  - `explain_decision`メソッドが、与えられたコンテキストに対して正しい判断と根拠を返すことを確認する。
  - パフォーマンスベンチマーク: 大量のログ生成がシステム全体の応答速度に与える影響を測定する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- `aegis_log.jsonl`のローテーションやアーカイブ戦略。
- 倫理原則の更新やバージョン管理のメカニズム。
- `explain_decision`の自然言語記述の品質と、その生成方法（テンプレート、LLM利用など）。
- 倫理原則IDとコード内のロジックの紐付けをどのように厳密に管理するか。

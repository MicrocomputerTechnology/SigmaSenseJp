# Phase 2.1: 使命の定義 (Mission Definition) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- 概要設計で言及された `orien_vision.py` は現在存在しないため、このフェーズで新規作成する。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `mission_statement.md`
  - プロジェクトのルート、または `/doc` ディレクトリに配置。
  - SigmaSenseJpの普遍的使命を記述する。
- **新規ファイル:** `src/orient/orien_vision.py`
  - Orienの中核的なビジョンを管理するモジュール。
  - 使命文を定数として保持し、他のモジュールから参照可能にする。

## 3. クラス/関数設計 (Class/Function Design)
### `mission_statement.md`
- Markdown形式で、以下の内容を記述する。
  - 使命のタイトル
  - 正式な使命文
  - 使命の背景と哲学的根拠（Issue #275より）
  - 使命がプロジェクトに与える影響

### `src/orient/orien_vision.py`
- **クラス:** `OrienVision` (仮)
  - **定数:** `UNIVERSAL_MISSION_STATEMENT`
    - Issue #275で定義された使命文を文字列として保持する。
  - **メソッド:** `get_mission_statement()`
    - `UNIVERSAL_MISSION_STATEMENT`を返す。
  - **メソッド:** `share_mission_to_party(party_id)` (仮)
    - 使命文を特定のパーティに共有する機能。具体的な実装は後続フェーズで検討。

## 4. データフロー (Data Flow)
- `mission_statement.md` は静的なドキュメントとして、プロジェクトの理念を明文化する。
- `src/orient/orien_vision.py` は、この使命文をコードレベルで保持し、他のモジュール（例: `MetaNarrator`, `Aegis`）がエージェントの行動や語りを生成する際に参照する。
- `README.md` から `mission_statement.md` へのリンクを設定し、プロジェクトの入り口で使命が提示されるようにする。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `README.md`: `mission_statement.md`へのリンクを追加。
- `src/orient/orien_vision.py`: 他のOrien関連モジュールや、物語生成 (`MetaNarrator`)、倫理判断 (`Aegis`) モジュールから、`OrienVision.get_mission_statement()` を通じて使命文を参照する。

## 6. テスト計画 (Test Plan)
- `mission_statement.md` が正しく作成され、内容がIssue #275の定義と一致することを確認する。
- `src/orient/orien_vision.py` が作成され、`UNIVERSAL_MISSION_STATEMENT` 定数が正しく定義されていることを確認する。
- `OrienVision.get_mission_statement()` メソッドが期待通りの使命文を返すことを確認する単体テストを作成する。
- `README.md` から `mission_statement.md` へのリンクが機能することを確認する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- `orien_vision.py` の具体的な配置場所（`src/orient/`直下か、サブディレクトリか）は、今後のOrien関連モジュールの設計と合わせて検討する。
- `share_mission_to_party` メソッドの具体的な実装（パーティへの伝達方法、タイミングなど）は、Phase 5.3「エージェント間インタラクション設計」で詳細化する。
- 使命文の変更管理（バージョン管理、更新プロセス）について検討する。

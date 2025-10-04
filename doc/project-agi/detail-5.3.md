# Phase 5.3: エージェント間インタラクション設計 (Agent Interaction Design) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `src/organization/agent_buffer.py` (仮)
  - モジュール間の情報伝達を管理するバッファ機能を提供する。
- **新規ファイル:** `src/organization/knowledge_activation_model.py` (仮)
  - 知識の活性化レベルを管理する。
- **新規ファイル:** `src/organization/mild_mother.py` (仮)
  - ミルドの母性機能（パーティ管理、労り、叱咤など）を実装する。
- **新規ファイル:** `src/organization/mild_insight.py` (仮)
  - ミルドの臨時メンバー導入能力を実装する。
- **新規ファイル:** `src/organization/external_members_db.py` (仮)
  - 臨時メンバーの情報を管理するデータベース。
- **既存ファイル修正:** `src/orient/orien_vision.py` (Phase 2.1で新規作成)
  - Orienの中枢モジュールとしての役割を強化。
- **既存ファイル修正:** `src/nova/meta_narrator.py`
  - ミルドとOrienの役割強化を反映した物語生成。
- **既存ファイル修正:** `src/hoho/pocket_library/unified_dictionary_service.py` (Phase 6で新規作成予定)
  - 知識の活性化モデルと連携。

## 3. クラス/関数設計 (Class/Function Design)
### `src/organization/agent_buffer.py`
- **クラス:** `AgentBuffer`
  - **メソッド:** `__init__(self, capacity: int = 100, transfer_rate: float = 1.0)`
    - バッファの容量と情報転送速度を設定。
  - **メソッド:** `send_message(self, sender_id: str, receiver_id: str, message: dict) -> bool`
    - メッセージをバッファに格納し、受信側へ転送。情報量の制限や転送速度の制約を適用。
  - **メソッド:** `receive_message(self, receiver_id: str) -> list[dict]`
    - 受信側がバッファからメッセージを取得。

### `src/organization/knowledge_activation_model.py`
- **クラス:** `KnowledgeActivationModel`
  - **メソッド:** `__init__(self, unified_dictionary_service: UnifiedDictionaryService)`
    - `UnifiedDictionaryService`のインスタンスを受け取る。
  - **メソッド:** `update_activation(self, knowledge_id: str, usage_event: str)`
    - 知識の利用頻度と経過時間に基づいて活性化レベルを更新。
  - **メソッド:** `get_activated_knowledge(self, query: str, threshold: float) -> list[str]`
    - 活性化レベルの高い知識を優先的に参照し、人間的な連想を再現。

### `src/organization/mild_mother.py`
- **クラス:** `MildMother`
  - **メソッド:** `__init__(self, world_model: WorldModel, pmg: PersonalMemoryGraph)`
    - `WorldModel`と`PersonalMemoryGraph`のインスタンスを受け取る。
  - **メソッド:** `optimize_party_formation(self, party_members: list[str]) -> list[str]`
    - パーティの特性（能力、負荷、相性、多様性）を洞察し、グループ編成を最適化。
  - **メソッド:** `intervene_party_member(self, member_id: str, intervention_type: str)`
    - 労り、叱咤、仲直り、視野拡大といった母性機能を発動。

### `src/organization/mild_insight.py`
- **クラス:** `MildInsight`
  - **メソッド:** `__init__(self, external_members_db: ExternalMembersDB)`
    - `ExternalMembersDB`のインスタンスを受け取る。
  - **メソッド:** `detect_special_case(self, context: dict) -> bool`
    - 特殊事案（例：`complexity_score>0.8`、大規模災害、倫理的ジレンマ）を検知。
  - **メソッド:** `introduce_temporary_member(self, party_id: str, member_type: str) -> str`
    - 臨時メンバー（子供達、使用人、外部専門家）をパーティに動的に組み込む。

### `src/organization/external_members_db.py`
- **クラス:** `ExternalMembersDB`
  - `src/hoho/pocket_library/database_handler.py`を基盤として、臨時メンバーの情報を管理するSQLiteデータベース。
  - **メソッド:** `add_member(self, member_data: dict)`
  - **メソッド:** `get_member(self, member_id: str)`

### `src/orient/orien_vision.py` (Phase 2.1で新規作成)
- **クラス:** `OrienVision`
  - **修正:** `receive_message(self, message: dict)` (新規メソッドとして追加)
    - `AgentBuffer`からメッセージを受け取るインターフェース。
  - **修正:** `send_strategic_insight(self, target_id: str, insight: dict)` (新規メソッドとして追加)
    - 高次の知性活動から得られた洞察を他のモジュールに伝達。

### `src/nova/meta_narrator.py`
- **クラス:** `MetaNarrator`
  - **修正:** ミルドとOrienの役割強化を反映した物語生成ロジックを追加。
    - ミルドの介入ログやパーティ編成の最適化を「人情劇」として語る。
    - Orienの戦略的洞察を「英雄譚」として編纂する。

## 4. データフロー (Data Flow)
- 各モジュールは`AgentBuffer`を介してメッセージを送受信する。
- `KnowledgeActivationModel`は`UnifiedDictionaryService`と連携し、知識の活性化レベルを管理する。
- `MildMother`は`WorldModel`と`PersonalMemoryGraph`からパーティの状態を洞察し、`AgentBuffer`を通じてパーティメンバーに介入する。
- `MildInsight`は特殊事案を検知し、`ExternalMembersDB`から臨時メンバーを選定し、`AgentBuffer`を通じてパーティに導入する。
- Orienは`AgentBuffer`から情報を受け取り、高次の知性活動を行い、その結果を`AgentBuffer`を通じて他のモジュールに伝達する。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `WorldModel` & `PersonalMemoryGraph`: `MildMother`がパーティの状態を洞察するために参照。
- `UnifiedDictionaryService` (#265, Phase 6): `KnowledgeActivationModel`が知識の活性化レベルを管理するために利用。
- `src/hoho/pocket_library/database_handler.py`: `ExternalMembersDB`の基盤として利用。
- `src/orient/orien_vision.py`: `AgentBuffer`との連携、Orienの中枢機能強化。

## 6. テスト計画 (Test Plan)
- `AgentBuffer`の単体テスト: メッセージの送受信、容量制限、転送速度の制約が正しく機能することを確認する。
- `KnowledgeActivationModel`の単体テスト: 知識の利用頻度と経過時間に基づいて活性化レベルが正しく更新され、優先順位付けが機能することを確認する。
- `MildMother`と`MildInsight`の単体テスト: パーティの最適化、介入、臨時メンバー導入が期待通りに機能することを確認する。
- 統合テスト: Orien、Mild、他のモジュールが`AgentBuffer`を介して協調し、パーティの健全な運営と特殊事案への対応が実現されることを確認する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- バッファのプロトコル設計: どのような情報が、どのような形式で、どのモジュール間でやり取りされるべきか。
- 知識の活性化レベルのチューニング: 人間的な連想を再現するための最適なパラメータ設定。
- 臨時メンバーの選定基準と、その導入・離脱プロセス。
- OrienとMildの役割分担における責任範囲の明確化と、競合発生時の解決メカニズム。

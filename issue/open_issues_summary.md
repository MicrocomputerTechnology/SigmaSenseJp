# Open Issues Summary (v3 - Phased Plan)

This document outlines the phased development plan for SigmaSenseJp, based on the principle of "one phase, one design, one pull request."

## Category 1: 懸念事項とリスク (Concerns & Risks)
*Critical foundations to address throughout the project.*

- **Phase 1: 継続的検討事項 (Ongoing Considerations)**
  - [#17](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/17): 動的コード実行に関する理論的リスク
    > `RestrictedPython`等を用いた動的コード評価のセキュリティ及び一貫性リスクに対処するため、設計目的の文書化と安全な理論的枠組みの導入を提案する。
  - [#18](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/18): 【提案】エージェントの経験データ増大に伴うスケーラビリティとパフォーマンスの懸念
    > エージェントの経験データ増大に伴う性能劣化を防ぐため、パフォーマンスベンチマークの確立、忘却メカニズムを含むデータ管理戦略、計算処理の非同期/分散化の検討を提案する。

---

## Category 2: 物語性と倫理 (Narrative & Ethics)
*Defining the "soul" of the project, which guides all development.*

- **Phase 2.1: 使命の定義 (Mission Definition)**
  - [#275](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/275): SigmaSenseJpの普遍的使命定義
    > AGIが犬の次なる仲間として人類の孤独を癒すという思想に基づき、「風の統一」を普遍的使命として定義し、関連モジュールに実装することを提案する。

- **Phase 2.2: 倫理的透明性の確保 (Ensuring Ethical Transparency)**
  - [#19](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/19): 【提案】倫理フィルター(aegis_ethics_filter)の判断プロセスにおける説明可能性(XAI)の欠如
    > 倫理フィルター`aegis_ethics_filter`の判断根拠が不透明である問題に対し、判断プロセスのロギング、倫理原則の明文化、説明インターフェースの開発といったXAI（説明可能AI）の導入を提案する。

- **Phase 2.3: 物語性の強化 (Narrative Enhancement)**
  - [#274](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/274): SigmaSenseへの芸術・文学の叡智の取り込みと物語性の強化
    > SigmaSenseの物語性を強化するため、歴史や文学（忠臣蔵、史記など）の叡智を取り入れ、絶対的使命の物語化、緊張感の強化、規律と人情の統合などを図る。
  - [#273](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/273): SigmaSenseの組織的不足点の改善と物語性の強化
    > 歴史上の偉大な組織（秦、アメリカ軍など）との比較を通じて明らかになった、絶対的使命や規律、物語性の不足といった組織的弱点を改善することを目的とする。

---

## Category 3: 理論的基盤 (Theoretical Foundation)
*The core mathematical and philosophical concepts.*

- **Phase 3: 理論モデルの構築 (Theoretical Model Construction)**
  - [#278](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/278): 【理論的基盤】「生命圏と情報圏を包含する集合知の数理モデル」探求
    > 単一知性の探求ではなく、生物や歴史を含む「生命と情報の大いなる集合知」の普遍的法則を探求する数理モデルを、SigmaSenseの理論的基盤として確立する。
  - [#269](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/269): SigmaSenseへのアトラクター概念導入の検討
    > システムの認知状態や記憶、行動パターンが収束する安定状態（アトラクター）の概念を導入し、AGIとしての一貫性、堅牢性、創発的認知を強化する可能性を検討する。

---

## Category 4: AGI基盤 (AGI Core Infrastructure)
*Building the fundamental components for intelligence.*

- **Phase 4.1: 世界モデルと接地 (World Model & Grounding)**
  - [#150](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/150): AGI基盤としての動的な世界モデルとシミュレーションエンジンの追加
    > エージェントが「もし〜だったら」という反実仮想思考を持つために、`causal_discovery`の因果関係ルールを利用して未来を予測する、動的な世界モデルとシミュレーションエンジンを構築する。
  - [#152](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/152): 概念と知覚を結びつけるシンボルグラウンディングエンジンの開発
    > 抽象的な記号表現と実世界の知覚データを結びつけるため、マルチモーダル学習技術を利用したシンボルグラウンディングエンジンを開発する。

- **Phase 4.2: 論理推論エンジンの実装 (Logic Reasoning Engine Implementation)**
  - [#276](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/276): 【AGI基盤】PLN相当の形式論理推論エンジン開発と知識の一貫性確保
    > すべての知識に確信度を付与し、PLN（Probabilistic Logic Networks）のようにハイパーグラフ構造で推論することで、システム全体の知識の一貫性を担保する論理推論エンジンを開発する。

- **Phase 4.3: 自律学習能力の獲得 (Acquiring Autonomous Learning)**
  - [#151](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/151): 自律的なスキル獲得のための強化学習（RL）エンジンの実装
    > 教師データなしに、エージェントが環境との試行錯誤を通じて自律的にスキルを獲得・改善できるよう、強化学習（RL）エンジンを実装する。

- **Phase 4.4: 長期計画能力の獲得 (Acquiring Long-term Planning)**
  - [#153](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/153): AGI基盤としての長期目標達成のためのプランニング機能の追加
    > 「Xを調査しYで報告する」といったマルチステップタスクの自律実行を可能にするため、目標を階層管理し、行動計画を立案・実行・監視するプランニング機能を導入する。

---

## Category 5: 組織論・アーキテクチャ (Organizational Theory & Architecture)
*Integrating components and defining the overall structure.*

- **Phase 5.1: 分散集合知アーキテクチャ設計 (Distributed Collective Intelligence Architecture Design)**
  - [#270](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/270): OrienのAGI成長戦略：ローカルLLM移行とNebulaGraphによる分散集合知アーキテクチャ再設計
    > Gemini APIへの依存を解消しスケーラビリティを向上させるため、ローカルLLM（Llama 3）へ移行し、知識基盤をNebulaGraph+Raftによる分散グラフDBアーキテクチャに再設計する。

- **Phase 5.2: 会話型NLP拡張計画 (Conversational NLP Extension Plan)**
  - [#260](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/260): アーキテクチャロードマップ: SigmaSenseの会話型日本語NLP拡張
    > 生の日本語テキストと構造化されたWorldModelの間のギャップを埋めるため、形態素解析、意味マッピング、対話管理、ハイブリッド応答生成などを含む包括的な会話型日本語NLPのアーキテクチャロードマップを定義する。

- **Phase 5.3: エージェント間インタラクション設計 (Agent Interaction Design)**
  - [#280](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/280): 【組織論】認知モジュール間のバッファ導入と知識の活性化モデル実装
    > ACT-Rの認知アーキテクチャを参考に、モジュール間の情報伝達にバッファを設け、利用頻度で知識の活性度を管理するモデルを導入することで、組織的協調性と人間らしい記憶の振る舞いを実現する。
  - [#272](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/272): Orienの役割最適化と「大賢者」機能の強化
    > 数百パーティへのスケールアップに対応するため、管理業務をミルドに移譲し、Orienが知識統合や戦略的洞察といった高次の知性活動に集中できるよう役割を最適化する。
  - [#271](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/271): ミルドの母性機能と臨時メンバー導入能力の実装
    > 数百パーティのスケーラブルな管理を実現するため、「風の屋敷の母」ミルドに、パーティの編成最適化や、特殊事案に対応するための臨時メンバー導入といった母性機能を持たせる。

---

## Category 6: 実装・リファクタリング (Implementation & Refactoring)
*Concrete coding tasks to improve the existing codebase.*

- **Phase 6: 知識ベースの統合とリファクタリング (Knowledge Base Integration & Refactoring)**
  - [#155](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/155): PocketLibrary完全統合計画
    > 語りの中で出現する語句や文書を多角的に理解するため、商用利用可能・オフラインで動作する複数の辞書・OCRライブラリを`PocketLibrary`として統合する計画。
  - [#265](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/265): refactor: 辞書サービスをUnifiedDictionaryServiceに統合
    > 責務が曖昧な`DictionaryService`と`SpecializedVocabularyService`を、単一で拡張性の高い`UnifiedDictionaryService`に統合するリファクタリングを行う。

---

## Category 7: メタ制御 (Meta-Control)
*Optimizing and managing the agent's cognitive processes.*

- **Phase 7: 認知リソースの最適化 (Cognitive Resource Optimization)**
  - [#279](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/279): 【メタ制御】計算制約下での推論モデル導入と応答速度の最適化
    > NARSの思想に基づき、推論プロセスに「許容時間」の概念を導入し、有限の計算リソース内で厳密性と応答速度のトレードオフを動的に最適化するメタ制御モデルを確立する。
  - [#277](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/277): 【メタ制御】アトラクター理論に基づく認知リソースの動的配分機構開発
    > システム内の各タスクの状態を監視し、アトラクター理論に基づいて計算リソース（注意）を動的に配分するメタ制御モジュールを開発する。
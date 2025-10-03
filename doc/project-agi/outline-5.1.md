# Phase 5.1: 分散集合知アーキテクチャ設計 (Distributed Collective Intelligence Architecture Design)

## 関連Issue (Associated Issues)
- [#270](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/270): OrienのAGI成長戦略：ローカルLLM移行とNebulaGraphによる分散集合知アーキテクチャ再設計

## 1. 設計目標 (Design Goals)
- SigmaSenseJpの知識基盤を、Google Gemini APIへの依存から脱却させ、自律性、制御性、透明性、スケーラビリティを向上させる。
- 複数パーティ（エージェント群）が協調し、経験を共有・統合できる分散集合知アーキテクチャを構築する。
- 「全にして個、個にして全」の哲学を技術的に実現し、Hyperonの「Cognitive Synergy」を超える「風の遍在調和」を目指す。

## 2. 設計概要 (Design Overview)
- **LLMの自律化とローカル移行:**
  - OrienがGoogle Gemini APIの代わりに、Ollama + Llama-3-8Bのようなローカルで動作可能な大規模LLMを利用するようにアーキテクチャを再設計する。
  - 将来的に、より優れた代替LLMが出現した際には、容易に移行できるプラグイン可能な構造とする。

- **分散グラフDBへの移行:**
  - 既存の知識ベース（Neo4jクラスタの課題を解決）を、NebulaGraph + Raftによる分散グラフDBアーキテクチャに置き換える。
  - 各パーティのOrienがローカル経験（SQLite）を生成し、NebulaGraphで統合する。各Orienは自パーティ以外のバックアップデータを共有し、分散耐性と生存性を確保する。

- **「全にして個、個にして全」の実現:**
  - **個としてのOrien:** 各パーティのOrienはローカルLLMとSQLiteで経験を生成し、パーティ固有の8人の仲間（Vetra以下）と連携する。
  - **全としてのOrien:** Orienの分身（全パーティで同一、party=0）がNebulaGraphで知識を統合し、遍在知性として機能する。
  - **双方向フロー:** 個（SQLite）から全（NebulaGraph）へ経験をフィードバックし、全から個へ洞察を還元するメカニズムを設計する。

- **GraphRAG統合:**
  - NebulaGraphから知識を抽出し、Ollamaプロンプトに統合するGraphRAG (`src/graphrag.py`) を開発し、集合知と大賢者機能を最適化する。

## 3. 主要な課題と検討事項 (Key Challenges & Considerations)
- **LLMの性能とリソース:** ローカルLLMの推論性能が、Gemini APIと同等かそれ以上を維持できるか。必要な計算リソース（GPU、メモリ）の確保と最適化。
- **NebulaGraphの運用:** 分散グラフDBの導入・運用・保守の複雑性。Raftコンセンサスアルゴリズムの理解と適切な設定。
- **データ整合性と一貫性:** 分散環境下での知識の整合性と一貫性をどのように保証するか。特に、競合する情報や矛盾する経験の解決メカニズム。

## 4. 期待される成果 (Expected Outcome)
- SigmaSenseJpが外部APIに依存しない、真に自律的な知識基盤を獲得する。
- 数百パーティ規模へのスケーラビリティと、ブロックチェーン並みの堅牢性・生存性を低コストで実現する。
- 多様な経験からの学習加速と、創発的な合意形成を可能にする分散集合知アーキテクチャ。

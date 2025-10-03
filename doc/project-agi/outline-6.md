# Phase 6: 知識ベースの統合とリファクタリング (Knowledge Base Integration & Refactoring)

## 関連Issue (Associated Issues)
- [#155](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/155): PocketLibrary完全統合計画
- [#265](https://github.com/MicrocomputerTechnology/SigmaSenseJp/issues/265): refactor: 辞書サービスをUnifiedDictionaryServiceに統合

## 1. 設計目標 (Design Goals)
- SigmaSenseが語りの中で出現する語句や画像・文書を、意味・翻訳・構造・定数・視覚語りとして多角的に理解・再構成できる、堅牢で統一された知識ベースを構築する。
- 辞書関連サービスのアーキテクチャを改善し、クリーンで拡張性の高い`UnifiedDictionaryService`に統合する。

## 2. 設計概要 (Design Overview)
- **`PocketLibrary`の完全統合:**
  - 商用利用可能・オフライン・Python対応の複数の辞書・OCRライブラリ（SudachiDict, UniDic, EJDict-hand, Argos Translate, SymPy, SciPy.constants, Astropy, 自作Python/哲学語彙辞典, YomiToku, Tesseract OCR, manga-ocr）を`PocketLibrary`として統合する。
  - 各ライブラリの機能を抽象化し、統一されたインターフェースを通じてアクセスできるようにする。

- **`UnifiedDictionaryService`の新設と統合:**
  - `src/pocket_library/`内に、すべての辞書・語彙リソースを管理する単一の`UnifiedDictionaryService`を作成する。
  - 既存の`DictionaryService`と`SpecializedVocabularyService`の機能を`UnifiedDictionaryService`に移植し、責務の曖昧さを解消する。
  - `SymbolicReasoner`が、新しく作成した`UnifiedDictionaryService`のみを利用するように修正する。
  - 統合完了後、古い`DictionaryService`と`SpecializedVocabularyService`をプロジェクトから削除する。

- **ダウンロードスクリプトの拡充:**
  - `scripts/download_models.py`に、`SudachiDict` (full版) と `Argos Translate` (日英・英日モデル) をダウンロードする機能を追加し、セットアッププロセスを簡素化する。

## 3. 主要な課題と検討事項 (Key Challenges & Considerations)
- **ライブラリ間の競合と互換性:** 多数の外部ライブラリを統合する際のバージョン管理、依存関係の解決、APIの統一。
- **性能最適化:** 複数の辞書やOCRエンジンを効率的に連携させ、応答速度を維持する。
- **知識表現の統一:** 異なる辞書や語彙リソースから得られる情報を、`WorldModel`や`SymbolicReasoner`が利用しやすい統一された形式で表現する。

## 4. 期待される成果 (Expected Outcome)
- SigmaSenseが語りや文書から、より深く、多角的な意味を抽出できるようになる。
- 辞書関連サービスのコードベースが整理され、メンテナンス性と拡張性が向上する。
- 外部リソースへの依存が明確化され、管理が容易になる。

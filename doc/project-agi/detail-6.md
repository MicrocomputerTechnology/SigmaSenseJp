# Phase 6: 知識ベースの統合とリファクタリング (Knowledge Base Integration & Refactoring) - 詳細設計

## 1. 概要設計からの変更点 (Changes from Overview Design)
- なし。概要設計の方向性で問題ない。

## 2. モジュール構成 (Module Structure)
- **新規ファイル:** `src/hoho/pocket_library/unified_dictionary_service.py`
  - 既存の`DictionaryService`と`SpecializedVocabularyService`の機能を統合する。
- **既存ファイル削除:** `src/hoho/pocket_library/dictionary_service.py`
  - `UnifiedDictionaryService`への統合後、削除。
- **既存ファイル削除:** `src/hoho/pocket_library/specialized_vocabulary_service.py`
  - `UnifiedDictionaryService`への統合後、削除。
- **既存ファイル修正:** `scripts/download_models.py`
  - `SudachiDict` (full版) と `Argos Translate` (日英・英日モデル) のダウンロード機能を追加。
- **既存ファイル修正:** `src/hoho/symbolic_reasoner.py`
  - `UnifiedDictionaryService`のみを利用するように修正。

## 3. クラス/関数設計 (Class/Function Design)
### `src/hoho/pocket_library/unified_dictionary_service.py`
- **クラス:** `UnifiedDictionaryService`
  - **メソッド:** `__init__(self, config: dict = None)`
    - `DictionaryService`と`SpecializedVocabularyService`が扱っていたすべての辞書・語彙リソース（Sudachi, MeCab, EJDict, WNJPN, Argos Translate, SymPy, SciPy.constants, Astropy, 自作Python/哲学語彙辞典, YomiToku, Tesseract OCR, manga-ocr）を内部で管理する。
    - 各リソースへのアクセスを抽象化し、統一されたインターフェースを提供する。
  - **メソッド:** `tokenize_japanese_text(self, text: str, mode: str = 'A') -> list`
    - Sudachi/MeCabを用いた日本語テキストの形態素解析。
  - **メソッド:** `lookup_english_word(self, word: str) -> list[tuple]`
    - EJDictを用いた英単語検索。
  - **メソッド:** `translate(self, text: str, from_lang: str, to_lang: str) -> str`
    - Argos Translateを用いた翻訳機能。
  - **メソッド:** `get_supertypes_from_wordnet(self, word: str) -> set`
    - WNJPNを用いた上位語（ハイパーニム）検索。
  - **メソッド:** `get_math_definition(self, symbol_string: str) -> dict`
    - SymPyを用いた数学記号の定義取得。
  - **メソッド:** `get_physics_constant(self, constant_name: str) -> dict`
    - SciPy/Astropyを用いた物理定数検索。
  - **メソッド:** `lookup_custom_term(self, term: str, vocab_type: str) -> list[tuple]`
    - 自作のPython/哲学語彙辞典検索。
  - **メソッド:** `perform_ocr(self, image_path: str, ocr_type: str) -> str`
    - YomiToku/Tesseract OCR/manga-ocrを用いたOCR機能。
  - **メソッド:** `close(self)`
    - すべてのデータベース接続を閉じる。

### `scripts/download_models.py`
- **関数:** `download_sudachi_dict()` (新規追加)
  - SudachiDict (full版) をダウンロードし、適切な場所に配置する。
- **関数:** `download_argos_translate_models()` (新規追加)
  - Argos Translateの日英・英日モデルをダウンロードし、インストールする。
- **修正:** `if __name__ == '__main__':` ブロック
  - 新しいダウンロード関数を呼び出すように修正。

### `src/hoho/symbolic_reasoner.py`
- **クラス:** `SymbolicReasoner`
  - **修正:** `__init__(self, world_model: WorldModel, unified_dictionary_service: UnifiedDictionaryService)`
    - `DictionaryService`の代わりに`UnifiedDictionaryService`のインスタンスを受け取るように変更。
  - **修正:** `_search_internal_dictionaries(self, word: str) -> set`
    - `UnifiedDictionaryService`のメソッドを利用するように変更。

## 4. データフロー (Data Flow)
- `scripts/download_models.py`が、必要な辞書・モデルをダウンロードし、`data/`ディレクトリに配置する。
- `UnifiedDictionaryService`が、これらのダウンロードされたリソースを抽象化されたインターフェースを通じて管理する。
- `SymbolicReasoner`や`JapaneseNLPFrontend` (#260, Phase 5.2) など、語彙やテキスト処理を必要とするモジュールは、`UnifiedDictionaryService`を通じて知識ベースにアクセスする。

## 5. 既存コードとの連携 (Integration with Existing Code)
- `src/hoho/pocket_library/dictionary_service.py`と`src/hoho/pocket_library/specialized_vocabulary_service.py`は削除される。
- `SymbolicReasoner`: `UnifiedDictionaryService`を利用するように依存関係を変更。
- `JapaneseNLPFrontend` (#260, Phase 5.2): `UnifiedDictionaryService`を利用するように設計。

## 6. テスト計画 (Test Plan)
- `UnifiedDictionaryService`の単体テスト: 統合されたすべての辞書・OCR機能が、統一されたインターフェースを通じて正しく動作することを確認する。
- `scripts/download_models.py`のテスト: 新しいダウンロード機能が正しく動作し、必要なアセットをダウンロードできることを確認する。
- `SymbolicReasoner`の統合テスト: `UnifiedDictionaryService`を通じて語彙検索や上位語取得が正しく行われることを確認する。
- パフォーマンスベンチマーク: 複数の辞書を横断検索する際の応答速度を測定し、最適化の必要性を評価する。

## 7. 考慮事項と未解決の課題 (Considerations & Open Questions)
- 多数の外部ライブラリのバージョン管理と依存関係の解決。
- 各ライブラリのライセンス（商用利用可能であること）の再確認。
- 知識表現の統一性: 異なる辞書からの情報を`WorldModel`が利用しやすい形式で表現するためのマッピング戦略。
- OCR機能の統合における画像前処理の標準化。

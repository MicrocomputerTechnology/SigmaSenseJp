# Hoho (ホーホー博士)

PocketLibraryを管理する賢いフクロウ。プロジェクトに蓄積された知識の化身。

このディレクトリには、システムの知識ベースへのアクセスを抽象化し、管理するモジュールが含まれています。

- **`pocket_library/`**: 複数の外部辞書（WordNet, EJDictなど）を統一的なインターフェースでラップするライブラリです。
- **`symbolic_reasoner.py`**: `WorldModel`や`PocketLibrary`の知識を利用して、観測された特徴に論理的な制約を与える推論エンジンです。
- **`proper_noun_store.py`**: 固有名詞を管理するストアです。
- **`knowledge_store_base.py`**: 知識ストアの基底クラスです。
- **`sqlite_knowledge_store.py`**: SQLiteを使用して知識を永続化する実装です。

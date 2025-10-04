# src/aegis

このディレクトリには、SigmaSenseJpの倫理フィルターであるAegis関連モジュールが含まれています。

## 関連設計ドキュメント
- **[Phase 2.2: 倫理的透明性の確保 - 詳細設計](../../doc/project-agi/detail-2.2.md)**

- **`aegis_ethics_filter.py`**: ミッションプロファイルに基づき、システムの行動が倫理規定に抵触しないか自律的に判断します。
- **`ethical_filter.py`**: 語りの安全性を検証し、不適切な内容を検知・無害化します。
- **`publication_gatekeeper.py`**: ミッションプロファイルに基づき、語りの公開可否を最終的に判断します。

# Nova (ノヴァ)

このディレクトリには、SigmaSenseJpの成長と物語生成を司るノヴァ関連モジュールが含まれています。

## 関連設計ドキュメント
- **[Phase 2.3: 物語性の強化 - 詳細設計](../../doc/project-agi/detail-2.3.md)**
- **[Phase 4.3: 自律学習能力の獲得 - 詳細設計](../../doc/project-agi/detail-4.3.md)**

意味の系譜化と語りの再構成を担う。時間軸を横断し、語りを継承する者。

このディレクトリには、システムの自己省察や成長、そしてそれを物語る（ナラティブ）機能に関連するモジュールが含まれています。

- **`growth_tracker.py`**: 過去の語りと比較し、新しい概念の獲得という「成長」を記録します。
- **`meta_narrator.py`**: 全経験を振り返り、自己の成長や心理状態の変化を「成長の物語」として生成します。
- **`narrative_analyzer.py`**: 語りの内容を分析します。
- **`narrative_hint_generator.py`**: 新しい語りのヒントを生成します。
- **`narrative_integrity.py`**: 語りの出典を記録し、追跡可能性を保証します。
- **`narrative_justifier.py`**: 判断の根拠を説明する「意図の語り」を生成します。
- **`intent_justifier.py`**: `narrative_justifier.py`と同様に、意図を説明する機能を持つと思われます。

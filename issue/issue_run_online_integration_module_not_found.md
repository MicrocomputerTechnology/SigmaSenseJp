# `run_online_integration.py`実行時のModuleNotFoundError

## 概要
`scripts/run_online_integration.py`スクリプトの実行中に、`gemini_client`モジュールが見つからないという`ModuleNotFoundError`が発生し、処理が異常終了しました。

## 発生事象
- **スクリプト:** `scripts/run_online_integration.py`
- **終了コード:** 1

## エラー詳細

### エラーメッセージ
```
Traceback (most recent call last):
  File "/sdcard/project/SigmaSenseJp/scripts/run_online_integration.py", line 3, in <module>
    from gemini_client import GeminiClient # オリエン大賢者をインポート
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'gemini_client'
```

### 考察
`run_online_integration.py`スクリプトは、プロジェクトのルートディレクトリから実行されています。一方で、インポートしようとしている`gemini_client.py`ファイルは`src`ディレクトリ内に配置されています。

Pythonのデフォルトの検索パスには`src`ディレクトリが含まれていないため、`from gemini_client import ...`という記述ではモジュールを見つけることができません。

## 推奨される対応
スクリプト内のインポート文を、`src`ディレクトリからの絶対パス形式に修正する必要があります。

**修正前 (3行目):**
```python
from gemini_client import GeminiClient
```

**修正案:**
```python
from src.gemini_client import GeminiClient
```
または、実行時に`PYTHONPATH`に`src`ディレクトリを追加するなどの環境設定も考えられます。

## Error: Missing Source Database in `src/stabilize_database.py`

When running `src/stabilize_database.py`, the script failed because the required source database file was not found.

### Error Message

```
🌿 差分補正によるデータベース安定化を開始します...
❗ エラー: ソースデータベースが見つかりません: /sdcard/project/SigmaSenseJp/config/sigma_product_database_custom_ai_generated.json
```

### Analysis

The `stabilize_database.py` script attempts to load a source database file from `config/sigma_product_database_custom_ai_generated.json`. This file is necessary for the stabilization process, and its absence causes the script to terminate with an error.

### Resolution

Before running `stabilize_database.py`, the source database needs to be built. This can typically be done by executing `src/build_database.py` to generate the `sigma_product_database_custom_ai_generated.json` file.

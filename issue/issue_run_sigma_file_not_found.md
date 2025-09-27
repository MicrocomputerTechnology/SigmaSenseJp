## Error: `FileNotFoundError` in `run_sigma.py`

When running `scripts/run_sigma.py`, a `FileNotFoundError` occurs because a required database file is missing.

### Error Message

```
FileNotFoundError: [Errno 2] No such file or directory: '/sdcard/project/SigmaSenseJp/config/sigma_product_database_custom_ai_generated.json'
```

### Analysis

The main script `run_sigma.py` attempts to load the SigmaSense database from `config/sigma_product_database_custom_ai_generated.json` using `src/sigma_database_loader.py`. However, this file does not exist in the specified path.

### Resolution

Before running `run_sigma.py`, the database needs to be built. This can typically be done by executing `src/build_database.py` to generate the `sigma_product_database_custom_ai_generated.json` file.
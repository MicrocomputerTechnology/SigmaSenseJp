## Error: `ValueError` in `tools/functor_consistency_checker.py`

When running `tools/functor_consistency_checker.py`, a `ValueError` occurs during the unpacking of values from `load_sigma_database`.

### Error Message

```
Traceback (most recent call last):
  File "/sdcard/project/SigmaSenseJp/tools/functor_consistency_checker.py", line 147, in <module>
    main()
  File "/sdcard/project/SigmaSenseJp/tools/functor_consistency_checker.py", line 67, in main
    database, ids, vectors = load_sigma_database(db_path)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### Analysis

The `load_sigma_database` function, called in `main` of `functor_consistency_checker.py`, is expected to return 3 values (`database`, `ids`, `vectors`). However, it appears to be returning a different number of values, leading to a `ValueError` during unpacking.

### Resolution

Inspect `src/sigma_database_loader.py` (where `load_sigma_database` is defined) to ensure it consistently returns exactly three values. If the function's signature or return values have changed, update the calling code in `tools/functor_consistency_checker.py` accordingly.

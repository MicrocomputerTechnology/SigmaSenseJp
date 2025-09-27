## Error: `ModuleNotFoundError` in `tools/semantic_axis_report.py`

When running `tools/semantic_axis_report.py`, a `ModuleNotFoundError` occurs because the `dimension_loader` module cannot be found.

### Error Message

```
Traceback (most recent call last):
  File "/sdcard/project/SigmaSenseJp/tools/semantic_axis_report.py", line 10, in <module>
    from src.semantic_axis_aggregator import aggregate_semantic_axes
  File "/sdcard/project/SigmaSenseJp/src/semantic_axis_aggregator.py", line 4, in <module>
    from dimension_loader import DimensionLoader
ModuleNotFoundError: No module named 'dimension_loader'
```

### Analysis

The `semantic_axis_report.py` script imports `aggregate_semantic_axes` from `src.semantic_axis_aggregator`, which in turn tries to import `DimensionLoader` from `dimension_loader`. The Python interpreter cannot find a module named `dimension_loader`.

This suggests an issue with the Python import path or the location of the `dimension_loader` module. Given the project structure, `dimension_loader` is likely located in `src/dimension_loader.py`, and should be imported as `from src.dimension_loader import DimensionLoader`.

### Resolution

Modify `src/semantic_axis_aggregator.py` to correctly import `DimensionLoader` from `src.dimension_loader`.

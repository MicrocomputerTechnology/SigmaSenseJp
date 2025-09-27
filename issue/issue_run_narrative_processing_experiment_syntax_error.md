## Error: `SyntaxError` in `run_narrative_processing_experiment.py`

When running `scripts/run_narrative_processing_experiment.py`, a `SyntaxError` occurs due to an unterminated string literal.

### Error Message

```
File "/sdcard/project/SigmaSenseJp/scripts/run_narrative_processing_experiment.py", line 183
    print("\n--- 実験終了 ---")======================")
                                                 ^
SyntaxError: unterminated string literal (detected at line 183)
```

### Analysis

Line 183 in `run_narrative_processing_experiment.py` contains a `print` statement with a string literal that is not properly terminated. It appears there's an extra `"` or a missing `+` for string concatenation.

### Resolution

Correct the syntax on line 183 of `scripts/run_narrative_processing_experiment.py` to properly terminate the string literal or correctly concatenate strings.
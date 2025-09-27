## Error: `TypeError` in `run_ethics_check_on_text.py`

When running `scripts/run_ethics_check_on_text.py`, a `TypeError` occurs.

### Traceback

```
Traceback (most recent call last):
  File "/sdcard/project/SigmaSenseJp/scripts/run_ethics_check_on_text.py", line 74, in <module>
    main()
  File "/sdcard/project/SigmaSenseJp/scripts/run_ethics_check_on_text.py", line 55, in main
    sigma = SigmaSense(database, ids, vectors, dimension_loader=loader)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: SigmaSense.__init__() missing 1 required positional argument: 'layers'
```

### Analysis

The `SigmaSense` class constructor `__init__` is missing the required positional argument `layers` when it is called in the `main` function of the script.

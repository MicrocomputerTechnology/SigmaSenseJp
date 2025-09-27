## Error: Missing Required Argument in `src/build_database.py`

When running `src/build_database.py`, the script failed due to a missing required command-line argument.

### Error Message

```
usage: build_database.py [-h] --img_dir IMG_DIR [--db_path DB_PATH]
                         [--dimension_config DIMENSION_CONFIG]
build_database.py: error: the following arguments are required: --img_dir
```

### Analysis

The `build_database.py` script requires the `--img_dir` argument to be provided when executed. This argument specifies the directory containing images to build the database from, and its absence causes the script to terminate with an error.

### Resolution

To run this script successfully, the `--img_dir` argument must be provided. For example:
`python src/build_database.py --img_dir sigma_images/`

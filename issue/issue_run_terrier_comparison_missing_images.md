## Error: Missing Image Files in `run_terrier_comparison.py`

When running `scripts/run_terrier_comparison.py`, the script failed to read required image files.

### Error Message

```
[ WARN:0@0.109] global loadsave.cpp:268 findDecoder imread_('sigma_images/dog_01.jpg'): can't open/read file: check file path/integrity
An error occurred in generate_terrier_vector for image sigma_images/dog_01.jpg: Image file could not be read: sigma_images/dog_01.jpg
[ WARN:0@0.110] global loadsave.cpp:268 findDecoder imread_('sigma_images/dog_02.jpg'): can't open/read file: check file path/integrity
An error occurred in generate_terrier_vector for image sigma_images/dog_02.jpg: Image file could not be read: sigma_images/dog_02.jpg
```

### Analysis

The script `run_terrier_comparison.py` attempts to load `sigma_images/dog_01.jpg` and `sigma_images/dog_02.jpg`, but these files are not found or cannot be read. This prevents the script from performing the terrier comparison.

### Resolution

Ensure that the image files `dog_01.jpg` and `dog_02.jpg` are present in the `sigma_images/` directory and are accessible.
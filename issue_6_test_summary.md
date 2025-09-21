# Issue #6: Sheaf Axioms Test Failure Summary

## Problem Description:
The `test_sheaf_axioms.py` was failing due to several issues related to dimension loading, database consistency, and hue calculation.

## Initial State of `tests/test_sheaf_axioms.py`:
- The test was attempting to verify the "gluing axiom" of sheaf theory by analyzing hue values of overlapping red and blue squares.
- It was loading the `sigma_product_database_custom_ai_generated.json` directly.

## Problems Encountered & Solutions Attempted:

1.  **`ModuleNotFoundError: No module named 'src'` (when running `tests/test_sheaf_axioms.py` directly):**
    -   **Cause:** The Python path was not correctly set up for direct execution of the test file, leading to issues with importing modules from the `src` directory.
    -   **Solution:** Modified `tests/test_sheaf_axioms.py` to correctly add the project root to `sys.path`, allowing relative imports from `src`. (This change was later reverted as part of a broader rollback.)

2.  **`ValueError: operands could not be broadcast together with shapes (66,) (33,)`:**
    -   **Cause:** The `DimensionLoader` was loading dimensions from `vector_dimensions_custom_ai_integrated.json` (which defines 66 dimensions), but the `sigma_product_database_custom_ai_generated.json` was built with an older set of dimensions (33 dimensions). This mismatch caused the `weighted_cosine_similarity` function to fail.
    -   **Solution:** Modified `tests/test_sheaf_axioms.py` to call `src.build_database.build_database()` in `setUpClass`. This was intended to ensure that a fresh database with the correct dimensions is built before the tests run. (This change was later reverted as part of a broader rollback.)

3.  **`TypeError: build_database() got an unexpected keyword argument 'output_path'`:**
    -   **Cause:** The `build_database()` function in `src/build_database.py` had a fixed signature and did not accept `output_path` and `img_dir` arguments.
    -   **Solution:** Modified `src/build_database.py` to accept `output_path` and `img_dir` as arguments, allowing the test to specify the temporary paths for the database and images. (This change was later reverted as part of a broader rollback.)

4.  **Incorrect Hue Detection for Blue Square (Hue 1.0 instead of ~0.67):**
    -   **Cause:** The `_calculate_shape_and_spatial_features` method in `sigma_image_engines/engine_opencv_legacy.py` was using a thresholding method on the L-channel that was not robust enough to correctly identify contours for the blue square, especially when it was the only colored object in the cropped image. This led to `dominant_hue_of_shapes` being incorrectly calculated as 0.0 (red).
    -   **Solution Attempt 1 (Reverted):** Changed thresholding to use Otsu's method on the saturation channel. This did not fully resolve the issue and sometimes resulted in hue 1.0 for blue.
    -   **Solution Attempt 2 (Reverted):** Combined L-channel and S-channel masks. This also did not fully resolve the issue.
    -   **Root Cause Identified:** The test setup itself was flawed. The "overlapping squares" test was creating cropped images for `r1` (red region) and `r2` (blue region) that *still contained parts of the other color*, leading to mixed hue values in `valid_h` and incorrect dominant hue calculations.

## Current Status:
All changes made during the debugging process have been reverted to restore the repository to a clean state. The test `test_sheaf_axioms.py` is still failing due to the fundamental issue of how the test images are generated and how the regions are defined. The current test setup with overlapping squares makes it difficult to isolate the hue of individual colors for accurate testing of the "gluing axiom".

## Next Steps (Proposed):
-   The test `test_gluing_semantic_consistency` needs to be re-evaluated. It might be better to test the hue detection on *isolated* color patches first, and then separately test the "gluing axiom" with a more robust method that doesn't rely on simple hue dominance in overlapping regions.
-   The `sigma_image_engines/engine_opencv_legacy.py` and `src/build_database.py` files are currently in their original state.

---
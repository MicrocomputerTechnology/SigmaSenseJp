import numpy as np
from collections import Counter
import cv2

def get_shape_invariant_key(contour, precision=1):
    """
    Calculates a shape descriptor key for a contour that is invariant to translation,
    scale, and rotation. This is achieved using Hu Moments, which are grounded in
    the principles of group theory (invariance under Euclidean group actions).

    Args:
        contour: The contour to analyze.
        precision: The decimal precision for rounding the log-transformed moments.

    Returns:
        A tuple representing the shape key, or None if the contour is invalid.
    """
    moments = cv2.moments(contour)
    if moments["m00"] == 0:
        return None
    
    # Hu Moments are invariant to translation, scale, and rotation.
    hu_moments = cv2.HuMoments(moments)
    
    # Log-transform to make the moments more comparable and scale-independent.
    # The absolute value is taken as the sign can change with reflections.
    log_hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments))
    
    # Round to the specified precision to create a robust key.
    return tuple(np.round(log_hu_moments, precision).flatten())

def detect_semantic_groups(regions):
    """
    Detects groups of objects with similar shapes using rotation- and scale-invariant
    Hu Moments, reflecting a group-theoretic approach to shape analysis.
    Returns the count of the largest group and its density.
    """
    if not regions or len(regions) < 2:
        return {"group_count": 0.0, "group_density": 0.0}

    # Generate a shape-invariant key for each region based on Hu Moments.
    keys = [get_shape_invariant_key(r['contour']) for r in regions]
    valid_keys = [k for k in keys if k is not None]

    if not valid_keys:
        return {"group_count": 0.0, "group_density": 0.0}

    # Find the most common shape key.
    freq = Counter(valid_keys)
    dominant_group = freq.most_common(1)[0]
    
    # A group must consist of at least 2 objects.
    group_count = dominant_group[1] if dominant_group[1] >= 2 else 0

    if group_count == 0:
        return {"group_count": 0.0, "group_density": 0.0}

    # Calculate the density of the dominant group.
    dominant_group_key = dominant_group[0]
    group_regions = [r for r, k in zip(regions, keys) if k == dominant_group_key]
    
    # Evaluate density using the minimum enclosing circle of the group.
    all_points = np.vstack([r['contour'] for r in group_regions])
    (x, y), radius = cv2.minEnclosingCircle(all_points)
    
    # Density = total area of group members / area of the enclosing circle
    group_area = sum(cv2.contourArea(r['contour']) for r in group_regions)
    enclosing_area = np.pi * radius**2
    density = group_area / enclosing_area if enclosing_area > 0 else 0.0

    # Normalize count (e.g., max out at 10 objects for a score of 1.0)
    normalized_count = min(group_count / 10.0, 1.0)

    return {
        "group_count": normalized_count,
        "group_density": density
    }

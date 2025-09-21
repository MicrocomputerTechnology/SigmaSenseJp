import numpy as np

class VectorTransforms:
    """
    Meaning vector transformations corresponding to image transformations.
    """
    def __init__(self, dimension_loader):
        self.dimension_loader = dimension_loader

    def rotate_hue_vector_transform(self, meaning_vector, angle_deg):
        """
        Simulates the effect of rotating an image on its hue dimension in the meaning vector.
        Assumes hue is represented in a circular 0-180 range.
        """
        hue_dim_id = "opencv_dominant_hue"
        hue_index = self.dimension_loader.get_index(hue_dim_id)

        if hue_index is None or hue_index >= len(meaning_vector):
            # Hue dimension not found or vector too small, return original vector
            return np.copy(meaning_vector)

        transformed_vector = np.copy(meaning_vector)
        original_hue = transformed_vector[hue_index]

        # Simulate hue shift (e.g., 180 degrees is a full circle for OpenCV hue)
        # A simple linear shift for now. More complex models might be needed for true functoriality.
        # For a 360-degree color wheel, 180 in OpenCV hue is 360 degrees.
        # So, a 90-degree image rotation might correspond to a 90-degree hue shift.
        # Let's assume a direct mapping for simplicity in this initial test.
        
        # Normalize angle to 0-180 range for OpenCV hue
        shifted_hue = (original_hue + angle_deg) % 180
        transformed_vector[hue_index] = shifted_hue

        return transformed_vector

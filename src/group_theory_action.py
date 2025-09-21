import numpy as np

class GroupAction:
    """
    Represents a group of transformations acting on a set of points.
    """
    def __init__(self, transformations):
        """
        Initializes the GroupAction with a list of transformation functions.

        Args:
            transformations: A list of functions, where each function represents a group element
                             (e.g., a rotation, translation). Each function should take a point
                             (e.g., a numpy array) and return the transformed point.
        """
        if not transformations:
            raise ValueError("Transformations list cannot be empty.")
        self.transformations = transformations

    def act(self, g, x):
        """
        Applies a group element 'g' to a point 'x'.

        Args:
            g: A transformation function from the group.
            x: The point (or object) to be transformed.

        Returns:
            The transformed point.
        """
        return g(x)

    def get_orbit(self, x, precision=5):
        """
        Calculates the orbit of a point 'x' under the group action.
        The orbit is the set of all points that can be reached from 'x' by applying
        all transformations in the group.

        Args:
            x: The starting point (must be a NumPy array).
            precision: The decimal precision for rounding to handle floating point inaccuracies.

        Returns:
            A set of points representing the orbit of 'x'. Using tuples for set hashing.
        """
        orbit = set()
        for g in self.transformations:
            transformed_point = self.act(g, x)
            # Round to a certain precision to handle floating point inaccuracies
            # and convert to tuple for hashability.
            rounded_point = tuple(np.round(transformed_point, decimals=precision))
            orbit.add(rounded_point)
        return orbit

    def get_stabilizer(self, x):
        """
        Calculates the stabilizer of a point 'x'.
        The stabilizer is the subgroup of transformations that leave the point 'x' unchanged.

        Args:
            x: The point for which to find the stabilizer.

        Returns:
            A list of transformation functions that form the stabilizer of 'x'.
        """
        stabilizer_group = []
        for g in self.transformations:
            if np.allclose(self.act(g, x), x):
                stabilizer_group.append(g)
        return stabilizer_group

# --- Example Transformation Groups ---

def get_rotation_group_2d(degrees=[90, 180, 270]):
    """
    Creates a list of 2D rotation transformations around the origin (0,0).
    Includes the identity transformation.
    """
    transformations = [lambda p: p]  # Identity
    for angle_deg in degrees:
        angle_rad = np.radians(angle_deg)
        # Use a closure to capture the rotation matrix for each angle
        def make_rotation(rad):
            rotation_matrix = np.array([
                [np.cos(rad), -np.sin(rad)],
                [np.sin(rad),  np.cos(rad)]
            ])
            return lambda p: rotation_matrix @ p
        transformations.append(make_rotation(angle_rad))
    return transformations

def get_translation_group_2d(translations):
    """
    Creates a list of 2D translation transformations.
    Includes the identity transformation.
    """
    transformations = [lambda p: p]  # Identity
    for t in translations:
        # Use a closure to capture the translation vector
        def make_translation(vec):
            translation_vector = np.array(vec)
            return lambda p: p + translation_vector
        transformations.append(make_translation(t))
    return transformations

def get_affine_group_2d(rotations_deg=[0], scales=[1.0], translations=[(0,0)], shears_deg=[0]):
    """
    Creates a list of 2D affine transformations.
    Each transformation is a combination of rotation, scaling, translation, and shear.
    Returns a list of functions that apply the affine transformation to a 2D point.
    """
    transformations = []
    for rot_deg in rotations_deg:
        for scale in scales:
            for trans_vec in translations:
                for shear_deg in shears_deg:
                    # Identity matrix
                    M = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)

                    # Apply rotation
                    rot_rad = np.radians(rot_deg)
                    R = np.array([
                        [np.cos(rot_rad), -np.sin(rot_rad), 0],
                        [np.sin(rot_rad),  np.cos(rot_rad), 0]
                    ])
                    M = R @ M # Apply rotation to identity

                    # Apply scaling
                    S = np.array([
                        [scale, 0, 0],
                        [0, scale, 0]
                    ])
                    M = S @ M # Apply scaling

                    # Apply shear (simple shear in x direction for now)
                    shear_rad = np.radians(shear_deg)
                    Sh = np.array([
                        [1, np.tan(shear_rad), 0],
                        [0, 1, 0]
                    ])
                    M = Sh @ M # Apply shear

                    # Apply translation
                    T = np.array([
                        [1, 0, trans_vec[0]],
                        [0, 1, trans_vec[1]]
                    ])
                    M = T @ M # Apply translation

                    # Create a function that applies this affine matrix to a point
                    def make_affine_transform(matrix):
                        return lambda p: (matrix @ np.array([p[0], p[1], 1.0]))[:2]
                    
                    transformations.append(make_affine_transform(M))
    return transformations

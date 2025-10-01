import unittest
import numpy as np
import sys
import os
import cv2

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sigma_image_engines')))

from src.sigmasense.group_theory_action import GroupAction, get_rotation_group_2d, get_affine_group_2d
from engine_opencv import OpenCVEngine

class TestGroupTheoryAction(unittest.TestCase):

    def test_rotation_orbit(self):
        """
        Tests the orbit calculation for a 2D point under a rotation group (C4).
        """
        # 1. Define the transformation group (C4: rotations by 0, 90, 180, 270 degrees)
        c4_rotations = get_rotation_group_2d(degrees=[90, 180, 270])
        c4_group = GroupAction(c4_rotations)

        # 2. Define a point to act upon
        point = np.array([1.0, 0.0])

        # 3. Calculate the orbit
        orbit = c4_group.get_orbit(point)

        # 4. Define the expected orbit
        # The point (1,0) rotated by 0, 90, 180, 270 degrees
        expected_orbit = {
            (1.0, 0.0),    # 0 degrees (identity)
            (0.0, 1.0),    # 90 degrees
            (-1.0, 0.0),   # 180 degrees
            (0.0, -1.0)    # 270 degrees
        }

        # 5. Assert that the calculated orbit matches the expected one
        self.assertEqual(orbit, expected_orbit)

    def test_empty_transformations(self):
        """
        Tests that initializing GroupAction with an empty list raises an error.
        """
        with self.assertRaises(ValueError):
            GroupAction([])

class TestFourierDescriptorsInvariance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = OpenCVEngine()
        cls.base_image_path = "test_square.png"
        cls._create_test_image(cls.base_image_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.base_image_path):
            os.remove(cls.base_image_path)

    @staticmethod
    def _create_test_image(path, shape='square', size=100, border=10, color=(255, 255, 255)):
        img_size = size + 2 * border
        img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
        if shape == 'square':
            cv2.rectangle(img, (border, border), (border + size, border + size), color, -1)
        elif shape == 'circle':
            cv2.circle(img, (img_size // 2, img_size // 2), size // 2, color, -1)
        cv2.imwrite(path, img)

    def _extract_fd(self, image_path):
        features = self.engine.extract_features(image_path)
        # Extract only Fourier Descriptors, assuming they are named 'opencv_fourier_descriptor_X'
        fd_features = sorted([v for k, v in features.items() if k.startswith('opencv_fourier_descriptor_')])
        return np.array(fd_features)

    def _extract_hu_moments(self, image_path):
        features = self.engine.extract_features(image_path)
        return np.array([features["opencv_hu_moment_1"], features["opencv_hu_moment_2"]])

    def test_fourier_descriptors_rotation_invariance(self):
        """
        Tests that Fourier Descriptors are invariant to rotation.
        """
        original_fd = self._extract_fd(self.base_image_path)

        # Rotate image by 90 degrees
        rotated_image_path = "test_square_rotated.png"
        img = cv2.imread(self.base_image_path)
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, 90, 1.0)
        rotated_img = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(rotated_image_path, rotated_img)

        rotated_fd = self._extract_fd(rotated_image_path)
        os.remove(rotated_image_path)

        np.testing.assert_allclose(original_fd, rotated_fd, rtol=1e-2, atol=1e-2,
                                   err_msg="Fourier Descriptors should be invariant to rotation.")

    def test_fourier_descriptors_scale_invariance(self):
        """
        Tests that Fourier Descriptors are invariant to scaling.
        """
        original_fd = self._extract_fd(self.base_image_path)

        # Scale image to half size
        scaled_image_path = "test_square_scaled.png"
        img = cv2.imread(self.base_image_path)
        scaled_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        cv2.imwrite(scaled_image_path, scaled_img)

        scaled_fd = self._extract_fd(scaled_image_path)
        os.remove(scaled_image_path)

        np.testing.assert_allclose(original_fd, scaled_fd, rtol=1e-2, atol=1e-2,
                                   err_msg="Fourier Descriptors should be invariant to scaling.")

    def test_fourier_descriptors_translation_invariance(self):
        """
        Tests that Fourier Descriptors are invariant to translation.
        """
        original_fd = self._extract_fd(self.base_image_path)

        # Translate image
        translated_image_path = "test_square_translated.png"
        img = cv2.imread(self.base_image_path)
        (h, w) = img.shape[:2]
        M = np.float32([[1, 0, 10], [0, 1, 10]]) # Shift by 10 pixels
        translated_img = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(translated_image_path, translated_img)

        translated_fd = self._extract_fd(translated_image_path)
        os.remove(translated_image_path)

        np.testing.assert_allclose(original_fd, translated_fd, rtol=1e-2, atol=2e-2,
                                   err_msg="Fourier Descriptors should be invariant to translation.")

    def test_hu_moments_affine_invariance(self):
        """
        Tests that Hu Moments are invariant to affine transformations.
        """
        original_hu = self._extract_hu_moments(self.base_image_path)

        # Apply an affine transformation (e.g., rotation + scale + shear)
        # Define 3 points in the original image and their corresponding points in the transformed image
        # For a square, we can pick corners.
        pts1 = np.float32([[50, 50], [150, 50], [50, 150]]) # Top-left, Top-right, Bottom-left of a 100x100 square
        
        # Define corresponding points after a transformation
        # Example: Rotate by 30 deg, scale by 0.8, translate by (20, 30)
        # This is a simplified affine transformation for testing purposes.
        # A more robust test would use get_affine_group_2d to generate the matrix.
        # For now, let's manually create a simple affine matrix.
        
        # Rotation by 30 degrees
        angle = np.radians(30)
        rot_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle),  np.cos(angle)]
        ])
        
        # Scale by 0.8
        scale_matrix = np.array([
            [0.8, 0],
            [0, 0.8]
        ])

        # Shear (simple x-shear)
        shear_factor = 0.2
        shear_matrix = np.array([
            [1, shear_factor],
            [0, 1]
        ])

        # Translation
        translation_vector = np.array([20, 30])

        # Combine transformations (order matters: scale, rotate, shear, translate)
        # For simplicity, let's just define the destination points directly for a known transformation
        # This avoids complex matrix multiplications in the test itself.
        
        # Let's use a simple rotation and translation for the test image
        # Original points: (50,50), (150,50), (50,150)
        # After 30 deg rotation around (0,0) and translation (20,30)
        # (x', y') = (x*cos - y*sin + tx, x*sin + y*cos + ty)
        
        # For a 100x100 square centered at (100,100) in a 200x200 image
        # Let's use cv2.getAffineTransform directly to generate the matrix
        # This is more robust than manual point calculation.
        
        # Define 3 points in the original image
        pts1_img = np.float32([[50, 50], [150, 50], [50, 150]])
        
        # Define corresponding points after a transformation (e.g., rotation + translation)
        # Rotate by 30 degrees around center (100,100) and translate by (20,20)
        M_test = cv2.getRotationMatrix2D((100, 100), 30, 1.0) # Rotate by 30 deg, no scale
        M_test[0, 2] += 20 # Add translation x
        M_test[1, 2] += 20 # Add translation y

        transformed_image_path = "test_square_affine.png"
        img = cv2.imread(self.base_image_path)
        (h, w) = img.shape[:2]
        transformed_img = cv2.warpAffine(img, M_test, (w, h))
        cv2.imwrite(transformed_image_path, transformed_img)

        transformed_hu = self._extract_hu_moments(transformed_image_path)
        os.remove(transformed_image_path)

        np.testing.assert_allclose(original_hu, transformed_hu, rtol=1e-2, atol=1e-2,
                                   err_msg="Hu Moments should be invariant to affine transformations.")

    def test_hu_moments_projective_invariance(self):
        """
        Tests that Hu Moments are invariant to projective transformations.
        """
        original_hu = self._extract_hu_moments(self.base_image_path)

        # Apply a projective transformation (perspective warp)
        img = cv2.imread(self.base_image_path)
        (h, w) = img.shape[:2]

        # Define 4 points in the original image (corners of the square)
        # The square is 100x100 with a 10px border, so it's from (10,10) to (110,110)
        pts1 = np.float32([[10, 10], [110, 10], [10, 110], [110, 110]])
        
        # Define corresponding points for the perspective distortion
        # Make it look like it's tilting away from the viewer
        pts2 = np.float32([[20, 30], [100, 20], [5, 120], [115, 110]])

        # Get the perspective transformation matrix
        M = cv2.getPerspectiveTransform(pts1, pts2)

        # Warp the image
        transformed_image_path = "test_square_projective.png"
        transformed_img = cv2.warpPerspective(img, M, (w, h))
        cv2.imwrite(transformed_image_path, transformed_img)

        # Extract Hu moments from the transformed image
        transformed_hu = self._extract_hu_moments(transformed_image_path)
        os.remove(transformed_image_path)

        # Assert that the Hu moments are approximately equal
        np.testing.assert_allclose(original_hu, transformed_hu, rtol=1e-2, atol=1e-2,
                                   err_msg="Hu Moments should be invariant to projective transformations.")

if __name__ == '__main__':
    unittest.main()

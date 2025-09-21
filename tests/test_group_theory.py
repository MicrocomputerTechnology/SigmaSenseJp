import unittest
import numpy as np
import sys
import os
import cv2

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sigma_image_engines')))

from group_theory_action import GroupAction, get_rotation_group_2d
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

if __name__ == '__main__':
    unittest.main()
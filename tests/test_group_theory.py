import unittest
import numpy as np
import sys
import os

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from group_theory_action import GroupAction, get_rotation_group_2d

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

if __name__ == '__main__':
    unittest.main()

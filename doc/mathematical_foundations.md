# Mathematical Foundations of SigmaSense

This document provides the formal definitions required by Issue #6, mapping the mathematical concepts used in this project to their concrete implementations in the code.

## 1. Group Theory

The concepts of group theory are used to handle transformations and invariants. The primary implementation can be found in `src/group_theory_action.py`.

| Mathematical Concept | Code Implementation | Description |
| :--- | :--- | :--- |
| **Group (G)** | `GroupAction` class | A class initialized with a list of transformation functions that represent the group elements. |
| **Group Element (g)** | A single transformation function | A function that takes a point (numpy array) and returns a transformed point. |
| **Group Action** | `GroupAction.act(g, x)` method | Applies a group element `g` to a point `x`. |
| **Orbit of x (Orbit(x))** | `GroupAction.get_orbit(x)` method | Calculates the set of all points reachable from `x` by applying all group transformations. |
| **Stabilizer of x (Stab(x))**| `GroupAction.get_stabilizer(x)` method | Calculates the subgroup of transformations that leave the point `x` invariant. |
| **Mathematical Test** | `tests/test_group_theory.py` | Verifies that the `get_orbit` method correctly computes the orbit for a point under the C4 rotation group, confirming adherence to the mathematical definition. |

## 2. Sheaf Theory

Sheaf theory is used to ensure that locally extracted features can be consistently combined into a global representation. The main logic is in `src/sheaf_analyzer.py` and `src/structure_detector.py`.

| Mathematical Concept | Code Implementation | Description |
| :--- | :--- | :--- |
| **Topological Space (X)** | The input image | The entire space on which the sheaf is defined. |
| **Open Set (U)** | A rectangular region `(x, y, w, h)` | A sub-region of the image on which local data (features) are defined. |
| **Section over U (F(U))** | A feature vector (numpy array) | The data associated with an open set, extracted by a feature generation engine for that image region. |
| **Restriction Map** | Cropping the image | The restriction of data from a larger set `U` to a smaller set `V` is implicitly handled by running feature extraction on the sub-image corresponding to `V`. |
| **Gluing Axiom (Semantic)** | `tests/test_sheaf_axioms.py` | This test provides a semantic, verifiable version of the gluing axiom. It checks that the feature vectors of two overlapping regions (`U1`, `U2`) are consistent with the feature vector of their intersection (`U12`). For example, if `U1` is red and `U2` is blue, the feature vector of the intersection `U12` should correspond to purple. This ensures local data is consistent on overlaps. |
| **Mathematical Test** | `tests/test_sheaf_axioms.py` | Verifies the semantic gluing axiom described above. |


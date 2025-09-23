
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import cv2
import numpy as np
from information_metrics import compute_kl_divergence, compute_wasserstein_distance

class OpenCVEngine:
    """
    Extracts features using traditional OpenCV methods.
    This engine handles foundational geometric and color analysis.
    """
    def __init__(self, config=None):
        """
        Initializes the OpenCV engine.
        
        Args:
            config (dict, optional): Configuration for the engine. Defaults to None.
        """
        print("Initializing OpenCV Engine...")
        self.config = config if config else {}

    def extract_features(self, image_data):
        """
        Extracts a set of features from an image using OpenCV.

        Args:
            image_data (np.ndarray): The image data as a NumPy array (BGR format).

        Returns:
            dict: A dictionary of extracted features with standard Python data types.
        """
        image = image_data

        # --- Feature extraction methods (can be expanded) ---
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Hu Moments for shape invariance
        moments = cv2.moments(gray)
        hu_moments = cv2.HuMoments(moments).flatten() # Flatten to a 1D array

        # Fourier Descriptors for shape invariance
        fourier_descriptors = self._extract_fourier_descriptors(gray)
        
        # Color Histograms
        # Convert BGR to RGB before converting to HSV
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        
        # Normalize histograms to probability distributions
        h_hist_prob = h_hist.flatten() / h_hist.sum() if h_hist.sum() > 0 else np.zeros_like(h_hist.flatten())
        s_hist_prob = s_hist.flatten() / s_hist.sum() if s_hist.sum() > 0 else np.zeros_like(s_hist.flatten())

        features = {
            "opencv_dominant_hue": int(np.argmax(h_hist)),
            "opencv_avg_saturation": float(np.mean(s_hist)),
            "opencv_edge_density": float(self._calculate_edge_density(image)),
            "opencv_h_hist_prob": h_hist_prob,
            "opencv_s_hist_prob": s_hist_prob,
        }

        # Add all 7 Hu Moments
        for i, hu_m in enumerate(hu_moments):
            features[f"opencv_hu_moment_{i+1}"] = float(hu_m)

        # Add Fourier Descriptors (e.g., first few magnitudes as features)
        for i, fd_mag in enumerate(fourier_descriptors[:5]): # Take first 5 magnitudes
            features[f"opencv_fourier_descriptor_{i+1}"] = float(fd_mag)
        
        return features

    def _calculate_edge_density(self, image):
        """
        Calculates the density of edges in the image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_count = np.count_nonzero(edges)
        image_area = image.shape[0] * image.shape[1]
        return edge_count / image_area if image_area > 0 else 0.0

    def _extract_fourier_descriptors(self, gray_image, num_descriptors=5):
        """
        Extracts Fourier Descriptors from the largest contour in a grayscale image.
        """
        _, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            return np.zeros(num_descriptors)

        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Resample contour to a fixed number of points for consistent FFT input
        # This helps with scale invariance if not handled by normalization later
        resampled_contour = self._resample_contour(largest_contour, 128) # e.g., 128 points

        # Convert contour points to complex numbers
        complex_contour = resampled_contour[:, 0, 0] + 1j * resampled_contour[:, 0, 1]

        # Apply FFT
        fft_result = np.fft.fft(complex_contour)

        # Take magnitudes and normalize for scale invariance
        # The first component (DC component) relates to position and size, so it's often ignored or normalized.
        # We normalize by the magnitude of the first non-zero component (or DC if all others are zero).
        magnitudes = np.abs(fft_result)
        
        # Normalize by the magnitude of the DC component (0th component) for scale invariance
        # Add a small epsilon to avoid division by zero
        dc_component_magnitude = magnitudes[0]
        if dc_component_magnitude < 1e-10:
            # If DC component is zero, normalize by the largest non-DC component, or return zeros
            if np.max(magnitudes[1:]) < 1e-10:
                return np.zeros(num_descriptors)
            else:
                magnitudes /= np.max(magnitudes[1:])
        else:
            magnitudes /= dc_component_magnitude

        # Fourier Descriptors are typically taken from the magnitudes, excluding the DC component
        # and often re-ordered to be rotation invariant (by shifting the sequence).
        # For simplicity, we'll take the first few non-DC magnitudes.
        # To make them rotation invariant, we can cyclically shift them so the largest magnitude (after DC) is first.
        # However, for basic feature extraction, just taking the magnitudes (excluding DC) is common.
        # We'll take the magnitudes from index 1 up to num_descriptors + 1.
        descriptors = magnitudes[1:num_descriptors + 1]
        
        return descriptors

    def _resample_contour(self, contour, num_points):
        """
        Resamples a contour to a fixed number of points using linear interpolation.
        """
        if len(contour) < 2:
            return np.zeros((num_points, 1, 2), dtype=np.int32)

        # Calculate cumulative arc length
        diffs = np.diff(contour[:, 0], axis=0)
        segment_lengths = np.sqrt(np.sum(diffs**2, axis=1))
        cumulative_lengths = np.concatenate(([0], np.cumsum(segment_lengths)))
        total_length = cumulative_lengths[-1]

        if total_length == 0:
            return np.zeros((num_points, 1, 2), dtype=np.int32)

        # Create equally spaced points along the contour
        interp_lengths = np.linspace(0, total_length, num_points)

        # Interpolate x and y coordinates
        interp_x = np.interp(interp_lengths, cumulative_lengths, contour[:, 0, 0])
        interp_y = np.interp(interp_lengths, cumulative_lengths, contour[:, 0, 1])

        resampled = np.vstack((interp_x, interp_y)).T
        return resampled.reshape(-1, 1, 2).astype(np.int32)

    def compare_images_probabilistically(self, image_data1, image_data2):
        """
        Compares two images based on their probabilistic feature distributions.
        """
        features1 = self.extract_features(image_data1)
        features2 = self.extract_features(image_data2)

        h_hist_prob1 = features1.get("opencv_h_hist_prob")
        s_hist_prob1 = features1.get("opencv_s_hist_prob")
        h_hist_prob2 = features2.get("opencv_h_hist_prob")
        s_hist_prob2 = features2.get("opencv_s_hist_prob")

        results = {}

        if h_hist_prob1 is not None and h_hist_prob2 is not None:
            results["h_hist_kl_divergence"] = compute_kl_divergence(h_hist_prob1, h_hist_prob2)
            results["h_hist_wasserstein_distance"] = compute_wasserstein_distance(np.arange(len(h_hist_prob1)), np.arange(len(h_hist_prob2)), u_weights=h_hist_prob1, v_weights=h_hist_prob2)
        
        if s_hist_prob1 is not None and s_hist_prob2 is not None:
            results["s_hist_kl_divergence"] = compute_kl_divergence(s_hist_prob1, s_hist_prob2)
            results["s_hist_wasserstein_distance"] = compute_wasserstein_distance(np.arange(len(s_hist_prob1)), np.arange(len(s_hist_prob2)), u_weights=s_hist_prob1, v_weights=s_hist_prob2)

        return results

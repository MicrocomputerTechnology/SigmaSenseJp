
import cv2
import numpy as np

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

    def extract_features(self, image_path):
        """
        Extracts a set of features from an image using OpenCV.

        Args:
            image_path (str): The path to the image file.

        Returns:
            dict: A dictionary of extracted features with standard Python data types.
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return {}

        # --- Feature extraction methods (can be expanded) ---
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Hu Moments for shape invariance
        moments = cv2.moments(gray)
        hu_moments = cv2.HuMoments(moments)
        
        # Color Histograms
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        
        features = {
            "opencv_hu_moment_1": float(hu_moments[0][0]),
            "opencv_hu_moment_2": float(hu_moments[1][0]),
            "opencv_dominant_hue": int(np.argmax(h_hist)),
            "opencv_avg_saturation": float(np.mean(s_hist)),
            "opencv_edge_density": float(self._calculate_edge_density(image)),
        }
        
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

if __name__ == '__main__':
    # Example usage
    engine = OpenCVEngine()
    # Create a dummy image for testing
    dummy_image_path = "test.png"
    cv2.imwrite(dummy_image_path, np.zeros((100, 100, 3), dtype=np.uint8))
    features = engine.extract_features(dummy_image_path)
    print("Extracted OpenCV features:")
    for name, value in features.items():
        print(f"  - {name}: {value}")

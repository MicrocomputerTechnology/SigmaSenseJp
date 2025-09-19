import numpy as np
import cv2
import json
import os
import sys
import signal

# Timeout mechanism to prevent hangs in OpenCV
class Timeout:
    def __init__(self, seconds=5, error_message='Processing timed out'):
        self.seconds = seconds
        self.error_message = error_message
    def _handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        # signal.SIGALRM is not available on Windows
        if sys.platform != "win32":
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        if sys.platform != "win32":
            signal.alarm(0) # Disable the alarm

def _calculate_ear_uprightness_score(gray_img, face_cascade):
    try:
        # 1. Detect face
        equalized_img = cv2.equalizeHist(gray_img)
        with Timeout(seconds=5, error_message="Face detection timed out in ear score calculation"):
            faces = face_cascade.detectMultiScale(equalized_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        
        if len(faces) == 0:
            return 0.0
        (x, y, w, h) = faces[0]

        # 2. Define ear ROI (region above the face)
        roi_y_start = max(0, y - h // 2)
        roi_y_end = y
        roi_x_start = max(0, x)
        roi_x_end = x + w
        
        ear_roi = gray_img[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        if ear_roi.size == 0:
            return 0.0

        # 3. Pre-process ROI to find contours
        blurred_roi = cv2.GaussianBlur(ear_roi, (5, 5), 0)
        _, thresh = cv2.threshold(blurred_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return 0.0

        # 5. Analyze contours to find the most "upright" one
        max_aspect_ratio = 0
        min_contour_area = (w * h) * 0.005 # Filter out tiny noise contours
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_contour_area:
                continue
            
            (cx, cy, cw, ch) = cv2.boundingRect(contour)
            
            if cw == 0:
                continue
                
            aspect_ratio = ch / cw
            if aspect_ratio > max_aspect_ratio:
                max_aspect_ratio = aspect_ratio

        # 6. Normalize the score
        # We'll assume an aspect ratio of 3.0 or more is a very upright ear (score 1.0)
        normalized_score = min(max_aspect_ratio / 3.0, 1.0)
        
        return normalized_score

    except TimeoutError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 0.0
    except Exception as e:
        print(f"Error in _calculate_ear_uprightness_score: {e}", file=sys.stderr)
        return 0.0

def _calculate_coat_texture_ruffness(gray_img, face_cascade):
    try:
        # 1. Detect face to locate the area around it
        with Timeout(seconds=5, error_message="Face detection timed out in coat texture calculation"):
            faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) == 0:
            # If no face, analyze the center of the image as a fallback
            h, w = gray_img.shape
            center_y, center_x = h // 2, w // 2
            roi = gray_img[center_y - h // 4 : center_y + h // 4, center_x - w // 4 : center_x + w // 4]
            if roi.size == 0:
                return 0.0
            laplacian_var = cv2.Laplacian(roi, cv2.CV_64F).var()
            # Normalize based on a heuristic maximum variance
            return min(laplacian_var / 500.0, 1.0)

        (x, y, w, h) = faces[0]

        # 2. Define ROIs for the coat (patches next to the face)
        rois = []
        # Left patch
        left_roi_x_start = max(0, x - w // 2)
        left_roi_x_end = x
        if left_roi_x_end > left_roi_x_start:
            rois.append(gray_img[y:y+h, left_roi_x_start:left_roi_x_end])
        
        # Right patch
        right_roi_x_start = x + w
        right_roi_x_end = min(gray_img.shape[1], x + w + w // 2)
        if right_roi_x_end > right_roi_x_start:
            rois.append(gray_img[y:y+h, right_roi_x_start:right_roi_x_end])

        if not rois:
            return 0.0

        # 3. Calculate the average Laplacian variance for the ROIs
        total_variance = 0
        for roi in rois:
            if roi.size > 0:
                total_variance += cv2.Laplacian(roi, cv2.CV_64F).var()
        
        avg_variance = total_variance / len(rois) if rois else 0.0

        # 4. Normalize the score
        # Heuristic: variance of 500 is considered very "ruff"
        normalized_score = min(avg_variance / 500.0, 1.0)
        
        return normalized_score

    except TimeoutError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 0.0
    except Exception as e:
        print(f"Error in _calculate_coat_texture_ruffness: {e}", file=sys.stderr)
        return 0.0

def _calculate_face_aspect_ratio(gray_img, face_cascade):
    try:
        # 1. Detect face
        with Timeout(seconds=5, error_message="Face detection timed out in face aspect ratio calculation"):
            faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) == 0:
            return 0.0 # Return 0.0 if no face is detected

        (x, y, w, h) = faces[0]

        # 2. Calculate aspect ratio
        if h == 0:
            return 0.0 # Avoid division by zero

        aspect_ratio = w / h

        # 3. Normalize the score
        # Heuristic: An aspect ratio of 2.0 or more is considered max (score 1.0)
        normalized_score = min(aspect_ratio / 2.0, 1.0)
        
        return normalized_score

    except TimeoutError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 0.0
    except Exception as e:
        print(f"Error in _calculate_face_aspect_ratio: {e}", file=sys.stderr)
        return 0.0

def _calculate_relative_muzzle_length(gray_img, face_cascade, eye_cascade):
    try:
        # 1. Detect face
        with Timeout(seconds=5, error_message="Face detection timed out in muzzle length calculation"):
            faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) == 0:
            return 0.5 # Return neutral score if no face

        (x, y, w, h) = faces[0]
        face_roi = gray_img[y:y+h, x:x+w]

        # 2. Detect eyes within the face
        with Timeout(seconds=2, error_message="Eye detection timed out in muzzle length calculation"):
            eyes = eye_cascade.detectMultiScale(face_roi)

        if len(eyes) < 2:
            return 0.5 # Not enough info, return neutral score

        # 3. Calculate average eye Y position (relative to the top of the face_roi)
        avg_eye_y = sum([ey for (ex, ey, ew, eh) in eyes]) / len(eyes)
        
        # 4. Calculate relative muzzle length
        # Muzzle starts below the eyes. Its height is relative to the whole face height.
        muzzle_start_y_in_face = avg_eye_y
        muzzle_height = h - muzzle_start_y_in_face
        
        if h == 0:
            return 0.5

        relative_length = muzzle_height / h
        
        # The score should be between 0 and 1, but clip just in case.
        return np.clip(relative_length, 0.0, 1.0)

    except TimeoutError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 0.5 # Return neutral score on timeout
    except Exception as e:
        print(f"Error in _calculate_relative_muzzle_length: {e}", file=sys.stderr)
        return 0.5

def _calculate_relative_eye_spacing(gray_img, face_cascade, eye_cascade):
    try:
        with Timeout(seconds=5, error_message="Object detection timed out in eye spacing calculation"):
            faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) == 0:
                return 0.5 # Return neutral: no face
            
            (x, y, w, h) = faces[0]
            face_roi = gray_img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(face_roi)
        
        # We need exactly two eyes to measure spacing
        if len(eyes) != 2:
            return 0.5 # Return neutral: not enough info

        # Sort eyes by x-coordinate to have a consistent order
        eyes = sorted(eyes, key=lambda eye: eye[0])
        
        eye1, eye2 = eyes
        
        # Calculate the center of each eye
        center1_x = eye1[0] + eye1[2] / 2
        center2_x = eye2[0] + eye2[2] / 2
        
        eye_distance = abs(center1_x - center2_x)
        
        # Normalize by face width
        if w == 0:
            return 0.5

        relative_spacing = eye_distance / w
        
        return np.clip(relative_spacing, 0.0, 1.0)

    except TimeoutError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 0.5 # Return neutral score on timeout
    except Exception as e:
        print(f"Error in _calculate_relative_eye_spacing: {e}", file=sys.stderr)
        return 0.5

def generate_terrier_vector(img_path, dim_path=None):
    # Define paths relative to this file's location
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_dir = os.path.join(project_root, 'config')

    if dim_path is None:
        dim_path = os.path.join(config_dir, "vector_dimensions_custom_ai_terrier.json")

    dimensions = []
    try:
        with open(dim_path, 'r', encoding='utf-8') as f:
            dimensions = json.load(f)
    except FileNotFoundError:
        print(f"Error: Dimension file not found: {dim_path}", file=sys.stderr)
        return []

    try:
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Image file could not be read: {img_path}")
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        cascade_path = os.path.join(config_dir, 'haarcascade_dog_face.xml')
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        cascades_path = os.path.join(os.path.dirname(cv2.__file__), 'data')
        eye_cascade_path = os.path.join(cascades_path, 'haarcascade_eye.xml')
        if not os.path.exists(eye_cascade_path):
            cascades_path = os.path.join(os.path.dirname(cv2.__file__), '..', '..', '..', '..', 'share', 'opencv4', 'haarcascades')
            eye_cascade_path = os.path.join(cascades_path, 'haarcascade_eye.xml')
            if not os.path.exists(eye_cascade_path):
                 raise FileNotFoundError(f"Could not find haarcascade_eye.xml in standard paths.")

        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        calculation_map = {
            "ear_uprightness_score": lambda: _calculate_ear_uprightness_score(gray_img, face_cascade),
            "coat_texture_ruffness": lambda: _calculate_coat_texture_ruffness(gray_img, face_cascade),
            "face_aspect_ratio": lambda: _calculate_face_aspect_ratio(gray_img, face_cascade),
            "relative_muzzle_length": lambda: _calculate_relative_muzzle_length(gray_img, face_cascade, eye_cascade),
            "relative_eye_spacing": lambda: _calculate_relative_eye_spacing(gray_img, face_cascade, eye_cascade),
        }

        meaning_vector = []
        for dim in dimensions:
            dim_id = dim['id']
            value = calculation_map.get(dim_id, lambda: 0.0)()
            meaning_vector.append(np.clip(value, 0.0, 1.0))

        return meaning_vector

    except Exception as e:
        print(f"An error occurred in generate_terrier_vector for image {img_path}: {e}", file=sys.stderr)
        return [0.0] * len(dimensions)

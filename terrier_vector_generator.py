import numpy as np
import cv2
import json

# --- Terrier Dimension Calculation Functions ---

def _calculate_ear_uprightness_score(gray_img, face_cascade):
    """
    Calculates the ear uprightness score based on the aspect ratio of the ear contour.
    """
    try:
        # 1. Preprocess image
        equalized_img = cv2.equalizeHist(gray_img)

        # 2. Detect face
        faces = face_cascade.detectMultiScale(equalized_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        if len(faces) == 0:
            return 0.0  # No face detected

        (x, y, w, h) = faces[0]

        # 3. Define ear ROIs
        top_margin = int(h * 0.6)
        side_margin = int(w * 0.05)
        ear_roi_width = int(w * 0.4)

        left_ear_roi_rect = (x + side_margin, y - top_margin, ear_roi_width, h)
        right_ear_roi_rect = (x + w - ear_roi_width - side_margin, y - top_margin, ear_roi_width, h)

        ratios = []
        for roi_rect in [left_ear_roi_rect, right_ear_roi_rect]:
            (rx, ry, rw, rh) = roi_rect
            rx, ry = max(0, rx), max(0, ry)
            rw, rh = min(rw, gray_img.shape[1] - rx), min(rh, gray_img.shape[0] - ry)
            
            ear_roi = equalized_img[ry:ry+rh, rx:rx+rw]
            if ear_roi.size < 50: continue

            # 4. Binarize and find contours
            _, binary_roi = cv2.threshold(ear_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: continue

            main_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(main_contour) < 50: continue

            # 5. Calculate aspect ratio of the minimum area rectangle
            rect = cv2.minAreaRect(main_contour)
            (w_rect, h_rect) = rect[1]

            if w_rect < 1 or h_rect < 1:
                continue

            aspect_ratio = max(w_rect, h_rect) / min(w_rect, h_rect)
            ratios.append(aspect_ratio)

        if not ratios:
            return 0.0

        # 6. Average and normalize
        avg_ratio = np.mean(ratios)
        # An upright ear should have a high ratio (e.g., > 2.5)
        # A round/floppy ear should have a ratio closer to 1.
        normalized_score = np.clip((avg_ratio - 1.0) / 2.5, 0.0, 1.0)
        return normalized_score

    except Exception as e:
        print(f"ERROR in _calculate_ear_uprightness_score: {e}")
        return 0.0

def _calculate_coat_texture_ruffness(gray_img, face_cascade):
    """
    Calculates the coat texture ruffness.
    """
    try:
        # 1. Define ROI based on face detection
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            # If no face, use the whole image as ROI
            roi = gray_img
        else:
            (x, y, w, h) = faces[0]
            # ROI around the face/cheeks
            roi_x = max(0, x - w//4)
            roi_y = max(0, y + h//2)
            roi_w = w + w//2
            roi_h = h//2
            roi = gray_img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

        if roi.size == 0:
            return 0.0

        # 2. Denoise
        blurred_roi = cv2.GaussianBlur(roi, (5, 5), 0)

        # 3. Sobel filter
        sobelx = cv2.Sobel(blurred_roi, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred_roi, cv2.CV_64F, 0, 1, ksize=3)

        # 4. Calculate magnitude
        magnitude = np.sqrt(sobelx**2 + sobely**2)

        # 5. Calculate mean
        mean_magnitude = np.mean(magnitude)

        # 6. Normalize
        # This normalization is empirical and might need adjustment
        normalized_score = np.clip((mean_magnitude - 20) / 80, 0.0, 1.0)
        return normalized_score

    except Exception as e:
        print(f"ERROR in _calculate_coat_texture_ruffness: {e}")
        return 0.0

def _calculate_face_aspect_ratio(gray_img, face_cascade):
    """
    Calculates the face aspect ratio.
    """
    try:
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return 0.0

        (x, y, w, h) = faces[0]
        if h == 0:
            return 0.0

        aspect_ratio = w / h
        # Normalize based on typical dog face ratios
        normalized_score = np.clip((aspect_ratio - 0.8) / 0.4, 0.0, 1.0)
        return normalized_score

    except Exception as e:
        print(f"ERROR in _calculate_face_aspect_ratio: {e}")
        return 0.0

def _calculate_relative_muzzle_length(gray_img, face_cascade):
    """
    Calculates the relative muzzle length.
    """
    try:
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return 0.0

        (x, y, w, h) = faces[0]
        
        # Fallback logic as described in algorithm_idea
        # Approximate nose position
        nose_y_approx = y + h * 0.75
        nose_h_approx = h * 0.1
        
        muzzle_length_approx = (y + h) - (nose_y_approx + nose_h_approx)
        if h == 0:
            return 0.0
            
        muzzle_length_ratio = muzzle_length_approx / h
        
        # Normalize
        normalized_score = np.clip((muzzle_length_ratio - 0.1) / 0.3, 0.0, 1.0)
        return normalized_score

    except Exception as e:
        print(f"ERROR in _calculate_relative_muzzle_length: {e}")
        return 0.0

def _calculate_relative_eye_spacing(gray_img, face_cascade, eye_cascade):
    """
    Calculates the relative eye spacing.
    """
    try:
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return 0.0

        (x, y, w, h) = faces[0]
        face_roi = gray_img[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(face_roi)
        
        if len(eyes) < 2:
            # Fallback logic
            left_eye_center_x = w * 0.3
            right_eye_center_x = w * 0.7
            eye_distance = abs(right_eye_center_x - left_eye_center_x)
        else:
            # Sort by x-coordinate to identify left and right eye
            eyes = sorted(eyes, key=lambda eye: eye[0])
            left_eye = eyes[0]
            right_eye = eyes[-1]
            
            left_eye_center_x = left_eye[0] + left_eye[2] / 2
            right_eye_center_x = right_eye[0] + right_eye[2] / 2
            eye_distance = abs(right_eye_center_x - left_eye_center_x)

        if w == 0:
            return 0.0

        eye_spacing_ratio = eye_distance / w
        
        # Normalize
        normalized_score = np.clip((eye_spacing_ratio - 0.3) / 0.3, 0.0, 1.0)
        return normalized_score

    except Exception as e:
        print(f"ERROR in _calculate_relative_eye_spacing: {e}")
        return 0.0

# --- Main Vector Generation Function ---

def generate_terrier_vector(img_path, dim_path="vector_dimensions_custom_ai_terrier.json"):
    """
    Generates a meaning vector for an image based on the terrier dimension definitions.
    """
    try:
        with open(dim_path, 'r', encoding='utf-8') as f:
            dimensions = json.load(f)
    except FileNotFoundError:
        print(f"❗ Error: Dimension definition file not found: {dim_path}")
        return []

    try:
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Image file could not be read: {img_path}")
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load cascades
        # Note: These paths might need to be adjusted depending on the environment
        face_cascade = cv2.CascadeClassifier('haarcascade_dog_face.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        calculation_map = {
            "ear_uprightness_score": lambda: _calculate_ear_uprightness_score(gray_img, face_cascade),
            "coat_texture_ruffness": lambda: _calculate_coat_texture_ruffness(gray_img, face_cascade),
            "face_aspect_ratio": lambda: _calculate_face_aspect_ratio(gray_img, face_cascade),
            "relative_muzzle_length": lambda: _calculate_relative_muzzle_length(gray_img, face_cascade),
            "relative_eye_spacing": lambda: _calculate_relative_eye_spacing(gray_img, face_cascade, eye_cascade),
        }

        meaning_vector = []
        for dim in dimensions:
            dim_id = dim['id']
            value = calculation_map.get(dim_id, lambda: 0.0)() # Default to 0.0 if function not found
            meaning_vector.append(np.clip(value, 0.0, 1.0))

        return meaning_vector

    except Exception as e:
        print(f"❗ Error during terrier vector generation ({img_path}): {e}")
        return [0.0] * len(dimensions)

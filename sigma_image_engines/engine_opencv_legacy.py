
import numpy as np
import cv2
import math
from skimage.feature import graycomatrix, graycoprops

class LegacyOpenCVEngine:
    """
    Extracts features using the original, detailed OpenCV methods from
    vector_generator.py (Selia) and lyra_vector_generator.py (Lyra).
    This engine handles the foundational geometric and perceptual dimensions.
    """
    def __init__(self, config=None):
        print("Initializing Legacy OpenCV Engine (Selia & Lyra)...")
        self.config = config if config else {}

    def extract_features(self, image_path):

        """
        Extracts a comprehensive set of features from an image using legacy OpenCV logic.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise FileNotFoundError(f"画像ファイルが読み込めませんでした: {image_path}")

            h, w, _ = img.shape
            img_area = h * w
            diagonal_length = math.sqrt(h**2 + w**2)

            # --- Common Preprocessing ---
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            lab_img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            l_channel, _, _ = cv2.split(lab_img)
            _, foreground_mask = cv2.threshold(l_channel, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(foreground_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            contours = [c for c in contours if cv2.contourArea(c) > 50]


            feature_map = {}

            # --- Execute all feature calculations ---
            self._calculate_selia_features(feature_map, img, gray_img, hsv_img, l_channel, contours, img_area, w, h, diagonal_length)
            self._calculate_lyra_features(feature_map, gray_img, hsv_img)

            return feature_map

        except Exception as e:
            print(f"❗ LegacyOpenCVEngineでエラーが発生しました ({image_path}): {e}")
            return {}

    def _calculate_selia_features(self, feature_map, img, gray_img, hsv_img, l_channel, contours, img_area, w, h, diagonal_length):

        """Calculates all Selia (structural) features."""
        self._calculate_color_features(feature_map, img, hsv_img)
        self._calculate_contrast_and_line(feature_map, l_channel, diagonal_length)
        self._calculate_shape_and_spatial_features(feature_map, contours, img, hsv_img, img_area, w, h, diagonal_length)

    def _calculate_lyra_features(self, feature_map, gray_img, hsv_img):

        """Calculates all Lyra (perceptual) features."""
        feature_map['contour_fluctuation'] = self._calculate_contour_fluctuation(gray_img)
        feature_map['edge_softness'] = self._calculate_edge_softness(gray_img)
        feature_map['motion_resonance'] = self._calculate_motion_resonance(gray_img)
        feature_map['gaze_impression'] = self._calculate_gaze_impression(gray_img)
        feature_map['form_presence'] = self._calculate_form_presence(hsv_img)
        feature_map['approachability'] = self._calculate_approachability(gray_img)
        feature_map['inner_vitality'] = self._calculate_inner_vitality(hsv_img, gray_img)
        feature_map['gracefulness'] = self._calculate_gracefulness(gray_img)


    # --- SELIA FEATURE HELPERS (from vector_generator.py) ---

    def _calculate_color_features(self, feature_map, img, hsv_img):

        try:
            _, _, v = cv2.split(hsv_img)
            feature_map['global_luminosity'] = np.mean(v) / 255.0

            s = hsv_img[:, :, 1]
            valid_s = s[s > 10]
            if len(valid_s) > 0:
                hist_s = cv2.calcHist([valid_s], [0], None, [256], [0, 256])
                peak_s = np.argmax(hist_s)
                feature_map['main_color_saturation'] = peak_s / 255.0
            else:
                feature_map['main_color_saturation'] = 0.0

            lab_img_color = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            a_channel, b_channel = lab_img_color[:, :, 1], lab_img_color[:, :, 2]
            hist_ab = cv2.calcHist([a_channel, b_channel], [0, 1], None, [32, 32], [0, 256, 0, 256])
            non_zero_bins = np.count_nonzero(hist_ab)
            feature_map['color_diversity_index'] = non_zero_bins / (32 * 32)
        except Exception:
            feature_map.update({'main_color_saturation': 0.0, 'global_luminosity': 0.0, 'color_diversity_index': 0.0})

    def _calculate_contrast_and_line(self, feature_map, l_channel, diagonal_length):

        try:
            feature_map['contrast_level'] = np.clip(np.std(l_channel) / 128.0, 0.0, 1.0)
            edges = cv2.Canny(l_channel, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)
            total_line_length = 0
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    total_line_length += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            max_expected_length = diagonal_length * 10
            feature_map['line_segment_density'] = np.clip(total_line_length / max_expected_length, 0.0, 1.0)
            angles = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angles.append(np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi % 180)
            if angles:
                hist, bins = np.histogram(angles, bins=18, range=(0, 180))
                feature_map['dominant_line_angle'] = bins[np.argmax(hist)] / 180.0
            else:
                feature_map['dominant_line_angle'] = 0.0
        except Exception:
            feature_map.update({'contrast_level': 0.0, 'line_segment_density': 0.0, 'dominant_line_angle': 0.0})

    def _calculate_shape_and_spatial_features(self, feature_map, contours, img, hsv_img, img_area, w, h, diagonal_length):
        shape_dim_ids = [
            'num_detected_shapes', 'average_circularity_index', 'average_rectangularity_index',
            'total_shape_area_ratio', 'centrality_of_shapes', 'vertical_balance_score',
            'horizontal_balance_score', 'overlap_degree', 'mean_color_saturation_of_shapes',
            'dominant_hue_of_shapes', 'aspect_ratio_consistency', 'density_of_small_shapes',
            'average_convexity_index', 'contour_roughness_score', 'alignment_strength'
        ]
        for dim_id in shape_dim_ids: feature_map[dim_id] = 0.0
        feature_map['aspect_ratio_consistency'] = 1.0
        feature_map['alignment_strength'] = 1.0

        num_contours = len(contours)
        if num_contours == 0:
            # If no contours are found, calculate dominant hue from the entire image
            h_channel = hsv_img[:, :, 0]
            if len(h_channel) > 0:
                hist_h = cv2.calcHist([h_channel], [0], None, [180], [0, 180])
                feature_map['dominant_hue_of_shapes'] = np.argmax(hist_h) / 179.0
            else:
                feature_map['dominant_hue_of_shapes'] = 0.0
            return

        feature_map['num_detected_shapes'] = np.clip(num_contours / 20.0, 0.0, 1.0)
        areas, circularities, rectangularities, convexities, aspect_ratios, roughnesses = [], [], [], [], [], []
        centroids, shape_masks = [], []
        total_shape_area = 0

        for c in contours:
            area = cv2.contourArea(c)
            if area < 50: continue
            total_shape_area += area
            areas.append(area)
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0: continue
            circularities.append((4 * np.pi * area) / (perimeter ** 2))
            try:
                _, (width, height), _ = cv2.minAreaRect(c)
                if width * height > 0:
                    rectangularities.append(area / (width * height))
                    aspect_ratios.append(max(width, height) / (min(width, height) + 1e-6))
            except: pass
            try:
                hull = cv2.convexHull(c)
                if cv2.contourArea(hull) > 0: convexities.append(area / cv2.contourArea(hull))
            except: pass
            approx = cv2.approxPolyDP(c, 0.01 * perimeter, True)
            roughnesses.append(abs(perimeter - cv2.arcLength(approx, True)) / perimeter)
            M = cv2.moments(c)
            if M["m00"] != 0: centroids.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask, [c], -1, 255, -1)
            shape_masks.append(mask)

        feature_map.update({
            'average_circularity_index': np.mean(circularities) if circularities else 0.0,
            'average_rectangularity_index': np.mean(rectangularities) if rectangularities else 0.0,
            'average_convexity_index': np.mean(convexities) if convexities else 0.0,
            'contour_roughness_score': np.mean(roughnesses) if roughnesses else 0.0,
            'aspect_ratio_consistency': 1.0 - np.clip(np.std(aspect_ratios) / 5.0, 0.0, 1.0) if len(aspect_ratios) > 1 else 1.0,
            'total_shape_area_ratio': total_shape_area / img_area,
            'density_of_small_shapes': len([a for a in areas if a / img_area < 0.005]) / num_contours if num_contours > 0 else 0.0
        })

        if centroids:
            center_x, center_y = w / 2, h / 2
            distances = [math.sqrt((cx - center_x)**2 + (cy - center_y)**2) for cx, cy in centroids]
            feature_map['centrality_of_shapes'] = 1.0 - np.clip(np.mean(distances) / (diagonal_length / 2.0), 0.0, 1.0)
            x_coords, y_coords = [c[0] for c in centroids], [c[1] for c in centroids]
            feature_map['horizontal_balance_score'] = 1.0 - np.clip(abs(np.mean(x_coords) - center_x) / (w / 2.0), 0.0, 1.0)
            feature_map['vertical_balance_score'] = 1.0 - np.clip(abs(np.mean(y_coords) - center_y) / (h / 2.0), 0.0, 1.0)
            feature_map['alignment_strength'] = 1.0 - np.clip(((np.std(x_coords) if len(x_coords) > 1 else 0) / (w/2) + (np.std(y_coords) if len(y_coords) > 1 else 0) / (h/2)) / 2.0, 0.0, 1.0)

        if shape_masks:
            combined_mask = np.zeros((h, w), dtype=np.uint8)
            for mask in shape_masks: combined_mask = cv2.bitwise_or(combined_mask, mask)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            hsv_img_rgb = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV)
            all_shape_pixels_hsv = cv2.bitwise_and(hsv_img, hsv_img, mask=combined_mask)
            # Debugging: Save hsv_img and combined_mask

            s_channel, h_channel = all_shape_pixels_hsv[:, :, 1], all_shape_pixels_hsv[:, :, 0]
            valid_pixels = s_channel > 10
            valid_s, valid_h = s_channel[valid_pixels], h_channel[valid_pixels]

            print(f"DEBUG: hsv_img shape: {hsv_img.shape}")
            print(f"DEBUG: combined_mask shape: {combined_mask.shape}")
            print(f"DEBUG: all_shape_pixels_hsv shape: {all_shape_pixels_hsv.shape}")
            print(f"DEBUG: h_channel unique values: {np.unique(h_channel)}")
            print(f"DEBUG: valid_h unique values: {np.unique(valid_h)}")

            feature_map['mean_color_saturation_of_shapes'] = np.mean(valid_s) / 255.0 if len(valid_s) > 0 else 0.0
            if len(valid_h) > 0:
                hist_h = cv2.calcHist([valid_h], [0], None, [180], [0, 180])
                print(f"DEBUG: hist_h argmax: {np.argmax(hist_h)}")
                print(f"DEBUG: hist_h max: {np.max(hist_h)}")
                feature_map['dominant_hue_of_shapes'] = np.argmax(hist_h) / 179.0
            else:
                feature_map['dominant_hue_of_shapes'] = 0.0
            if len(shape_masks) > 1:
                union_area = np.count_nonzero(combined_mask)
                feature_map['overlap_degree'] = np.clip((total_shape_area - union_area) / (total_shape_area + 1e-6), 0.0, 1.0)
            else:
                feature_map['overlap_degree'] = 0.0

    # --- LYRA FEATURE HELPERS (from lyra_vector_generator.py) ---

    def _calculate_contour_fluctuation(self, gray_img):
        try:
            blurred_img = cv2.medianBlur(gray_img, 5)
            binary_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: return 0.0
            main_contour = max(contours, key=cv2.contourArea)
            contour_length = cv2.arcLength(main_contour, True)
            if contour_length == 0: return 0.0
            hull = cv2.convexHull(main_contour)
            hull_length = cv2.arcLength(hull, True)
            if hull_length == 0: return 0.0
            return np.clip(((contour_length / hull_length) - 1.0) * 2.0, 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_edge_softness(self, gray_img):
        try:
            sobel_x = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            soft_edge_threshold = 50
            soft_pixels = np.sum(magnitude < soft_edge_threshold)
            return np.clip(soft_pixels / gray_img.size, 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_motion_resonance(self, gray_img):
        try:
            laplacian_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
            return np.clip(1.0 - (laplacian_var / 1000.0), 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_gaze_impression(self, gray_img):
        try:
            h, w = gray_img.shape
            center_roi = gray_img[h//4:h*3//4, w//4:w*3//4]
            if center_roi.size == 0: return 0.0
            contrast = center_roi.std()
            brightness = center_roi.mean()
            _, highlight_mask = cv2.threshold(center_roi, 240, 255, cv2.THRESH_BINARY)
            highlight_ratio = np.count_nonzero(highlight_mask) / center_roi.size
            return np.clip(((contrast / 100.0) + (brightness / 255.0) + (highlight_ratio * 3.0)) / 3.0, 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_form_presence(self, hsv_img):
        try:
            v_channel = hsv_img[:, :, 2]
            hist, _ = np.histogram(v_channel, bins=256, range=(0, 256))
            dark_pixels = np.sum(hist[:25])
            bright_pixels = np.sum(hist[230:])
            contrast_strength = (dark_pixels + bright_pixels) / v_channel.size
            std_dev = v_channel.std()
            return np.clip((contrast_strength * 5.0) + (std_dev / 100.0), 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_approachability(self, gray_img):
        try:
            blurred_img = cv2.medianBlur(gray_img, 5)
            circles = cv2.HoughCircles(blurred_img, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=10, maxRadius=100)
            circle_score = np.clip(len(circles) / 10.0, 0.0, 1.0) if circles is not None else 0.0
            contours, _ = cv2.findContours(cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: return circle_score
            main_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(main_contour)
            if area == 0: return circle_score
            perimeter = cv2.arcLength(main_contour, True)
            if perimeter == 0: return circle_score
            circularity = 4 * np.pi * area / (perimeter**2)
            return np.clip((circle_score + circularity) / 2.0, 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_inner_vitality(self, hsv_img, gray_img):
        try:
            s_channel, v_channel = hsv_img[:, :, 1], hsv_img[:, :, 2]
            mean_saturation = s_channel.mean() / 255.0
            value_diversity = v_channel.std() / 100.0
            glcm = graycomatrix(cv2.convertScaleAbs(gray_img), distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
            energy = graycoprops(glcm, 'energy')[0, 0]
            texture_richness = np.clip(energy * 5.0, 0.0, 1.0)
            return np.clip((mean_saturation + value_diversity + texture_richness) / 3.0, 0.0, 1.0)
        except Exception: return 0.0

    def _calculate_gracefulness(self, gray_img):
        try:
            edges = cv2.Canny(gray_img, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: return 0.0
            total_smoothness, total_length = 0, 0
            for cnt in contours:
                length = cv2.arcLength(cnt, False)
                if length > 50:
                    approx = cv2.approxPolyDP(cnt, 0.02 * length, False)
                    smoothness = 1.0 - np.clip(len(approx) / (length / 10.0 + 1e-6), 0.0, 1.0)
                    total_smoothness += smoothness * length
                    total_length += length
            if total_length == 0: return 0.0
            return np.clip(total_smoothness / total_length, 0.0, 1.0)
        except Exception: return 0.0

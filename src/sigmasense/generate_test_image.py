import cv2
import numpy as np
import os

os.makedirs("sigma_images", exist_ok=True)

# 1. 中央の円（circle_center.jpg）
img1 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.circle(img1, (128, 128), 40, (0, 0, 0), -1)
cv2.imwrite("sigma_images/circle_center.jpg", img1)

# 2. 左側の四角（square_left.jpg）
img2 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.rectangle(img2, (60, 100), (120, 160), (0, 0, 0), -1)
cv2.imwrite("sigma_images/square_left.jpg", img2)

# 3. 上部の三角（triangle_top.jpg）
img3 = np.ones((256, 256, 3), dtype=np.uint8) * 255
pts = np.array([[128, 40], [88, 100], [168, 100]], np.int32)
cv2.drawContours(img3, [pts], 0, (0, 0, 0), -1)
cv2.imwrite("sigma_images/triangle_top.jpg", img3)

# 4. 中央の五角形 (pentagon_center.jpg)
img4 = np.ones((256, 256, 3), dtype=np.uint8) * 255
center_x, center_y = 128, 128
radius = 50
pts = []
for i in range(5):
    angle = i * 2 * np.pi / 5 - np.pi / 2
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    pts.append([x, y])
cv2.drawContours(img4, [np.array(pts)], 0, (0, 0, 0), -1)
cv2.imwrite("sigma_images/pentagon_center.jpg", img4)

# 5. 中央の六角形 (hexagon_center.jpg)
img5 = np.ones((256, 256, 3), dtype=np.uint8) * 255
center_x, center_y = 128, 128
radius = 50
pts = []
for i in range(6):
    angle = i * 2 * np.pi / 6
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    pts.append([x, y])
cv2.drawContours(img5, [np.array(pts)], 0, (0, 0, 0), -1)
cv2.imwrite("sigma_images/hexagon_center.jpg", img5)

# 6. 5光星 (star_five.jpg)
img6 = np.ones((256, 256, 3), dtype=np.uint8) * 255
center_x, center_y = 128, 128
outer_radius = 60
inner_radius = 25
pts = []
for i in range(10):
    radius = outer_radius if i % 2 == 0 else inner_radius
    angle = i * np.pi / 5 - np.pi / 2
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    pts.append([x, y])
cv2.drawContours(img6, [np.array(pts)], 0, (0, 0, 0), -1)
cv2.imwrite("sigma_images/star_five.jpg", img6)

# 7. 垂直線 (line_vertical.jpg)
img7 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.line(img7, (128, 40), (128, 216), (0, 0, 0), 5)
cv2.imwrite("sigma_images/line_vertical.jpg", img7)

# 8. 曲線 (curve_arc.jpg)
img8 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.ellipse(img8, (128, 128), (80, 50), 0, 180, 360, (0, 0, 0), 5)
cv2.imwrite("sigma_images/curve_arc.jpg", img8)

# 9. 中央の赤い円 (circle_center_red.jpg)
img9 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.circle(img9, (128, 128), 40, (0, 0, 255), -1)
cv2.imwrite("sigma_images/circle_center_red.jpg", img9)

# 10. 中央の青い五角形 (pentagon_center_blue.jpg)
img10 = np.ones((256, 256, 3), dtype=np.uint8) * 255
center_x, center_y = 128, 128
radius = 50
pts = []
for i in range(5):
    angle = i * 2 * np.pi / 5 - np.pi / 2
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    pts.append([x, y])
cv2.drawContours(img10, [np.array(pts)], 0, (255, 0, 0), -1)
cv2.imwrite("sigma_images/pentagon_center_blue.jpg", img10)

# --- 追加の画像 ---

# 11. 対角線 (line_diagonal.jpg)
img11 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.line(img11, (40, 40), (216, 216), (0, 0, 0), 5)
cv2.imwrite("sigma_images/line_diagonal.jpg", img11)

# 12. 緑の上部の三角 (triangle_top_green.jpg)
img12 = np.ones((256, 256, 3), dtype=np.uint8) * 255
pts = np.array([[128, 40], [88, 100], [168, 100]], np.int32)
cv2.drawContours(img12, [pts], 0, (0, 255, 0), -1)
cv2.imwrite("sigma_images/triangle_top_green.jpg", img12)

# 13. 複数オブジェクト (multi_object.jpg)
img13 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.circle(img13, (80, 80), 30, (0, 0, 0), -1)
cv2.rectangle(img13, (150, 150), (200, 200), (0, 0, 0), -1)
cv2.imwrite("sigma_images/multi_object.jpg", img13)

# 14. 重なり合うオブジェクト (overlap_object.jpg)
img14 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.circle(img14, (110, 128), 40, (0, 0, 0), -1)
cv2.rectangle(img14, (100, 100), (180, 160), (0, 0, 0), -1)
cv2.imwrite("sigma_images/overlap_object.jpg", img14)

# 15. 水平線 (line_horizontal.jpg)
img15 = np.ones((256, 256, 3), dtype=np.uint8) * 255
cv2.line(img15, (40, 128), (216, 128), (0, 0, 0), 5)
cv2.imwrite("sigma_images/line_horizontal.jpg", img15)

print("15種類のテスト画像を sigma_images/ に生成しました。")
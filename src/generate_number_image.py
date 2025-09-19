import numpy as np
import cv2
import os
import sys

def generate_number_image(number_text, output_path):
    """Generates an image of a given number and saves it to the specified path."""
    # Define image properties
    width, height = 100, 100
    image = np.zeros((height, width), dtype=np.uint8)

    # Define the number properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    font_thickness = 3
    text_size = cv2.getTextSize(number_text, font, font_scale, font_thickness)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2

    # Put the text on the image
    cv2.putText(image, number_text, (text_x, text_y), font, font_scale, 255, font_thickness)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the image
    cv2.imwrite(output_path, image)
    print(f"Image of '{number_text}' saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_number_image.py <number> <output_path>")
        sys.exit(1)

    number_to_generate = sys.argv[1]
    file_path = sys.argv[2]
    
    generate_number_image(number_to_generate, file_path)
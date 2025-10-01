# Handles Optical Character Recognition (OCR) services.
from PIL import Image
import pytesseract
from yomitoku import Yomitoku
from manga_ocr import MangaOcr

class OCRService:
    """Provides a unified interface for various OCR engines."""

    def __init__(self):
        """Initializes the OCR services."""
        try:
            self.manga_ocr_engine = MangaOcr()
        except Exception as e:
            print(f"Failed to initialize MangaOcr: {e}")
            self.manga_ocr_engine = None
        
        try:
            self.yomitoku_engine = Yomitoku()
        except Exception as e:
            print(f"Failed to initialize Yomitoku: {e}")
            self.yomitoku_engine = None

    def extract_text_tesseract(self, image_path: str, lang: str = 'eng+jpn') -> str:
        """
        Extracts text from an image using Tesseract OCR.

        Args:
            image_path: Path to the image file.
            lang: Language for OCR (e.g., 'eng', 'jpn', 'eng+jpn').

        Returns:
            The extracted text as a string.
        """
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img, lang=lang)
                return text
        except FileNotFoundError:
            return f"Error: Image file not found at {image_path}"
        except Exception as e:
            return f"An error occurred with Tesseract: {e}"

    def extract_text_yomitoku(self, image_path: str) -> str:
        """
        Extracts text from a document image using Yomitoku.

        Args:
            image_path: Path to the image file.

        Returns:
            The extracted text as a Markdown string.
        """
        if not self.yomitoku_engine:
            return "Error: Yomitoku engine not initialized."
        try:
            with Image.open(image_path) as img:
                return self.yomitoku_engine(img)
        except FileNotFoundError:
            return f"Error: Image file not found at {image_path}"
        except Exception as e:
            return f"An error occurred with Yomitoku: {e}"

    def extract_text_manga_ocr(self, image_path: str) -> str:
        """
        Extracts text from a manga image using MangaOcr.

        Args:
            image_path: Path to the image file.

        Returns:
            The extracted text.
        """
        if not self.manga_ocr_engine:
            return "Error: MangaOcr engine not initialized."
        try:
            with Image.open(image_path) as img:
                return self.manga_ocr_engine(img)
        except FileNotFoundError:
            return f"Error: Image file not found at {image_path}"
        except Exception as e:
            return f"An error occurred with MangaOcr: {e}"

# Example usage:
if __name__ == '__main__':
    # Note: These examples require Tesseract to be installed on the system.
    # They also require appropriate image files with text.
    # Using a simple geometric image will likely result in empty strings.
    service = OCRService()
    example_image = "sigma_images/circle_center.jpg"

    print(f"--- OCR on image: {example_image} ---")

    print("\n--- Tesseract ---")
    tesseract_text = service.extract_text_tesseract(example_image)
    print(f"Extracted: '{tesseract_text.strip()}'")

    print("\n--- Yomitoku ---")
    yomitoku_text = service.extract_text_yomitoku(example_image)
    print(f"Extracted: '{yomitoku_text.strip()}'")

    print("\n--- MangaOcr ---")
    manga_ocr_text = service.extract_text_manga_ocr(example_image)
    print(f"Extracted: '{manga_ocr_text.strip()}'")
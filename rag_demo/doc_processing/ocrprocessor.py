from PIL import Image
from PIL import Image
import pytesseract
from .base import DocProcessor

class OCRDecorator(DocProcessor):
    def __init__(self, base_processor: DocProcessor):
        super().__init__(base_processor.file_path)
        self.base = base_processor
        self._ocr_text = None  # Cache OCR result
        self._ocr_used = False

    def extract_text(self) -> str:
        if self._ocr_text is not None:
            return self._ocr_text

        if self.file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                print("Process image")
                image = Image.open(self.file_path)
                print("Image opened successfully")
                text = pytesseract.image_to_string(image)
                print("OCR completed")
                print("End Processing image")
                if text.strip():
                    self._ocr_used = True
                    self._ocr_text = text
                    return text
                else:
                    self._ocr_text = self.base.extract_text()
                    return self._ocr_text
            except Exception as e:
                # Optionally log the exception here
                # print(f"OCR failed for {self.file_path}: {e}")
                self._ocr_text = self.base.extract_text()
                return self._ocr_text
        else:
            print(f"Exception during OCR processing: {e}")
            self._ocr_text = self.base.extract_text()
            return self._ocr_text

    def get_type(self) -> str:
        if self._ocr_used:
            return self.base.get_type() + " (OCR)"
        else:
            return self.base.get_type()

    def extract_metadata(self) -> dict:
        base_meta = self.base.extract_metadata()
        if self._ocr_used:
            base_meta["ocr_used"] = True
        else:
            base_meta["ocr_used"] = False
        return base_meta
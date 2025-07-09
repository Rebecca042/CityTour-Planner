from PIL import Image
from PIL import Image
import pytesseract
from .base import DocProcessor

class OCRDecorator(DocProcessor):
    def __init__(self, base_processor: DocProcessor):
        super().__init__(base_processor.file_path)
        self.base = base_processor

    def extract_text(self) -> str:
        # Nur bei bestimmten Dateitypen OCR versuchen
        if self.file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                image = Image.open(self.file_path)
                text = pytesseract.image_to_string(image)
                return text if text.strip() else self.base.extract_text()
            except Exception:
                return self.base.extract_text()
        # Für PDFs oder andere Dateitypen aktuell Fallback
        return self.base.extract_text()

    def get_type(self) -> str:
        return self.base.get_type() + " (OCR)"

    def extract_metadata(self) -> dict:
        base_meta = self.base.extract_metadata()
        base_meta["ocr_used"] = True
        return base_meta
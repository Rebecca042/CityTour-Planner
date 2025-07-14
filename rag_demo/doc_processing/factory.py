# doc_processing/factory.py
import logging
from typing import Union

from .rechnung import RechnungProcessor
from .postkarte import PostkarteProcessor
from .tagebuch import TagebuchProcessor
from .broschuere import BroschuereProcessor
from .fallback import FallbackProcessor
from .ocrprocessor import OCRDecorator
from .dummy_processor import DummyProcessor  # importiere den DummyProcessor


class DocProcessorFactory:
    def __init__(self, use_dummy=False, ocr_enabled=True, ocr_filetypes=None):
        self.use_dummy = use_dummy
        self.ocr_enabled = ocr_enabled
        self.ocr_filetypes = ocr_filetypes or [".jpg", ".jpeg", ".png"]
        self._mapping = {
            "rechnung": RechnungProcessor,
            "postkarte": PostkarteProcessor,
            "tagebuch": TagebuchProcessor,
            "broschuere": BroschuereProcessor,
        }

    def detect_doc_type(self, file_path: str) -> Union[str, None]:
        path_lower = file_path.lower()
        for key in self._mapping:
            if key in path_lower:
                return key
        return None

    def needs_ocr(self, file_path: str) -> bool:
        if not self.ocr_enabled:
            return False
        return any(file_path.lower().endswith(ext) for ext in self.ocr_filetypes)

    def get_processor(self, file_path: str):
        if self.use_dummy:
            return DummyProcessor(file_path)

        doc_type = self.detect_doc_type(file_path)
        if doc_type:
            base_processor = self._mapping[doc_type](file_path)
        else:
            base_processor = FallbackProcessor(file_path)

        if self.needs_ocr(file_path):
            print("Using OCRDecorator")
            return OCRDecorator(base_processor)
        return base_processor





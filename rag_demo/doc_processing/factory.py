# doc_processing/factory.py
import logging

from .rechnung import RechnungProcessor
from .postkarte import PostkarteProcessor
from .tagebuch import TagebuchProcessor
from .broschuere import BroschuereProcessor
from .fallback import FallbackProcessor
from .ocrprocessor import OCRDecorator
from .dummy_processor import DummyProcessor  # importiere den DummyProcessor

class DocProcessorFactory:
    _mapping = {
        "rechnung": RechnungProcessor,
        "postkarte": PostkarteProcessor,
        "tagebuch": TagebuchProcessor,
        "broschuere": BroschuereProcessor,
    }

    @staticmethod
    def get_processor(file_path: str):
        # Für den ersten Test immer DummyProcessor zurückgeben
        return DummyProcessor(file_path)

    @staticmethod
    def get_processor_advanced(file_path: str):
        path_lower = file_path.lower()
        for key, processor in DocProcessorFactory._mapping.items():
            if key in path_lower:
                base_processor = processor(file_path)
                if DocProcessorFactory._needs_ocr(file_path):
                    logging.info(f"Applying OCRDecorator to {file_path}")
                    return OCRDecorator(base_processor)
                else:
                    return base_processor
        # Fallback mit Info
        logging.warning(f"Unknown document type for {file_path}, using FallbackProcessor")
        fallback = FallbackProcessor(file_path)
        if DocProcessorFactory._needs_ocr(file_path):
            logging.info(f"Applying OCRDecorator to fallback processor for {file_path}")
            return OCRDecorator(fallback)
        return fallback

    @staticmethod
    def _needs_ocr(file_path: str) -> bool:
        # OCR nur bei Bilddateien (PDF evtl. gesondert behandeln)
        return file_path.lower().endswith((".jpg", ".jpeg", ".png"))




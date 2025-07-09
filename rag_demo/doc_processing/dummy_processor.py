from .base import DocProcessor
from .dummy_data_provider import get_dummy_text, get_dummy_metadata
import os

class DummyProcessor(DocProcessor):
    def extract_text(self) -> str:
        return get_dummy_text(self.file_path)

    def get_type(self) -> str:
        name = os.path.basename(self.file_path).lower()
        if "rechnung" in name:
            return "Rechnung"
        elif "ticket" in name:
            return "Ticket"
        elif "tagebuch" in name:
            return "Tagebuch"
        elif "postkarte" in name:
            return "Postkarte"
        elif "broschuere" in name:
            return "Broschüre"
        elif "speisekarte" in name:
            return "Speisekarte"
        else:
            return "Fallback"

    def extract_metadata(self) -> dict:
        return get_dummy_metadata(self.file_path)

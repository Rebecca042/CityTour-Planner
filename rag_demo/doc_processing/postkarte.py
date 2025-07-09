from .base import DocProcessor
from langchain_community.document_loaders import PyPDFLoader

class PostkarteProcessor(DocProcessor):
    def extract_text(self) -> str:
        # Beispiel: Postkarten sind oft Bilder mit Text (OCR nötig)
        # Hier vereinfacht: Text aus PDF laden (oder OCR-Integration später)
        loader = PyPDFLoader(self.file_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    def get_type(self) -> str:
        return "Postkarte"

    def extract_metadata(self) -> dict:
        return {
            "absender": "Unbekannt",
            "ort": "Gardasee (vermutet)",
        }
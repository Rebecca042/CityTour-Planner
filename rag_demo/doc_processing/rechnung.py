# doc_processing/rechnung.py
import re
from .base import DocProcessor
from langchain_community.document_loaders import PyPDFLoader

class RechnungProcessor(DocProcessor):
    def extract_text(self) -> str:
        loader = PyPDFLoader(self.file_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    def get_type(self) -> str:
        return "Rechnung"

    def extract_metadata(self) -> dict:
        text = self.extract_text()
        betrag = re.search(r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})\s*€)", text)
        datum = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
        return {
            "betrag": betrag.group(1) if betrag else None,
            "datum": datum.group(0) if datum else None,
            "quelle": "aus Rechnung",
        }

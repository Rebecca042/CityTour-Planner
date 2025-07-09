# rag_demo/document_overview.py

import os

class DocumentOverviewBuilder:
    def __init__(self, processor):
        self.processor = processor

    def build_overview(self) -> dict:
        text = self.processor.extract_text() or ""
        meta = self.processor.extract_metadata() or {}

        return {
            "filename": os.path.basename(self.processor.file_path),
            "file_type": self.processor.get_type(),
            "text_excerpt": (text[:200].strip() + ("..." if len(text) > 200 else "")) if text else "",
            "metadata": meta,
            "ocr_used": meta.get("ocr_used", False),
            "icon": self._get_icon(self.processor.get_type()),
            # Optional: weitere Metadatenfelder hier ergänzen, z.B. Datum, Autor etc.
        }

    def _get_icon(self, file_type: str) -> str:
        icons = {
            "Rechnung": "🧾",
            "Postkarte": "📮",
            "Tagebuch": "📓",
            "Broschüre": "📘",
            "Speisekarte": "📜",  # z. B.
            "Ticket": "🎫",  # z. B.
            "Fallback": "📂",
        }
        # OCR-Zusatz entfernen, damit das Icon korrekt erkannt wird
        clean_type = file_type.replace(" (OCR)", "")
        return icons.get(clean_type, "📁")


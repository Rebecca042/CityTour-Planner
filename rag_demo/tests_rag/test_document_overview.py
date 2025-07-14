import pytest
from rag_demo.document_overview import DocumentOverviewBuilder
from doc_processing.base import DocProcessor

class DummyProcessor(DocProcessor):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def extract_text(self) -> str:
        # Langer Text (>200 Zeichen) zum Testen des Excerpts
        return "Dies ist ein langer Testtext. " * 15

    def get_type(self) -> str:
        return "Rechnung"

    def extract_metadata(self) -> dict:
        return {"ocr_used": True, "author": "Rebecca"}

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        self._file_path = value


def test_build_overview_basic():
    processor = DummyProcessor("/pfad/zu/einer/rechnung_test.pdf")
    builder = DocumentOverviewBuilder(processor)
    overview = builder.build_overview()

    assert overview["filename"] == "rechnung_test.pdf"
    assert overview["file_type"] == "Rechnung"
    assert overview["ocr_used"] is True
    assert "author" in overview["metadata"]
    assert overview["metadata"]["author"] == "Rebecca"
    assert overview["icon"] == "🧾"
    assert overview["text_excerpt"].endswith("...")  # Kürzung geprüft
    assert len(overview["text_excerpt"]) <= 203  # 200 chars + "..."


def test_build_overview_empty_text_and_metadata():
    class EmptyProcessor(DocProcessor):
        def __init__(self, file_path: str):
            self._file_path = file_path

        def extract_text(self) -> str:
            return ""

        def get_type(self) -> str:
            return "Fallback"

        def extract_metadata(self) -> dict:
            return {}

        @property
        def file_path(self) -> str:
            return self._file_path

        @file_path.setter
        def file_path(self, value: str):
            self._file_path = value

    processor = EmptyProcessor("/pfad/zu/unknown_file.dat")
    builder = DocumentOverviewBuilder(processor)
    overview = builder.build_overview()

    assert overview["filename"] == "unknown_file.dat"
    assert overview["file_type"] == "Fallback"
    assert overview["ocr_used"] is False
    assert overview["text_excerpt"] == ""
    assert overview["icon"] == "📂"

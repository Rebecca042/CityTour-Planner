import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..doc_processing.factory import DocProcessorFactory
from ..doc_processing.rechnung import RechnungProcessor
from ..doc_processing.postkarte import PostkarteProcessor
from ..doc_processing.tagebuch import TagebuchProcessor
from ..doc_processing.broschuere import BroschuereProcessor
from ..doc_processing.fallback import FallbackProcessor

# Test für bekannte Dokumenttypen
@pytest.mark.parametrize("filename,expected_class", [
    ("rechnung_01.pdf", RechnungProcessor),
    ("POSTKARTE_urlaub.pdf", PostkarteProcessor),
    ("tagebuch_2023.pdf", TagebuchProcessor),
    ("broschuere_garten.pdf", BroschuereProcessor),
])
def test_get_processor_known_types(filename, expected_class):
    processor = DocProcessorFactory.get_processor(filename)
    assert isinstance(processor, expected_class), f"{filename} sollte {expected_class.__name__} liefern"

# Test für unbekannte Dokumente mit fallback
def test_get_processor_fallback():
    processor = DocProcessorFactory.get_processor("unbekanntes_dokument.pdf")
    assert isinstance(processor, FallbackProcessor), "Unbekannte Dateien sollten FallbackProcessor verwenden"

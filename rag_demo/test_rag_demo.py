import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .rag_demo_minimal import narrate

def test_narrate_contains_keyword():
    result = narrate()
    assert "Rebecca" in result or "LLM" in result, "Erwartetes Stichwort fehlt im Ergebnis"

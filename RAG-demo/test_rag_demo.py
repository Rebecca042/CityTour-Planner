from rag_demo import narrate

def test_narrate_contains_keyword():
    result = narrate()
    assert "Rebecca" in result or "LLM" in result, "Erwartetes Stichwort fehlt im Ergebnis"

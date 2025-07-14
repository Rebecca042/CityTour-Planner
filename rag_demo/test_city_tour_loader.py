# test_city_tour_loader.py
import os

from doc_processing.factory import DocProcessorFactory
from rag_demo.city_tour_loader import CityTourLoader
import os


def test_load_paris_tour():
    # Absoluter Pfad relativ zum Testskript
    base_dir = os.path.dirname(__file__)
    folder_path = os.path.join(base_dir, "docs", "paris")

    folder_path = os.path.abspath(folder_path)  # Optional, nur um sicherzugehen

    assert os.path.exists(folder_path), f"Ordner {folder_path} existiert nicht"

    factory = DocProcessorFactory(use_dummy=True)  # falls so konstruiert

    loader = CityTourLoader(folder_path, factory)
    overviews = loader.load_all_overviews()

    assert isinstance(overviews, list), "Erwartet wird eine Liste von Overviews"
    assert len(overviews) > 0, "Es sollten Overviews geladen werden"
    print("Overviews:")
    print(overviews)
    for overview in overviews:
        assert isinstance(overview, dict), "Jede Übersicht sollte ein Dictionary sein"
        # Statt 'title' oder 'summary' prüfen wir auf 'filename' und 'text_excerpt'
        assert "filename" in overview, "Overview sollte 'filename' enthalten"
        assert "text_excerpt" in overview, "Overview sollte 'text_excerpt' enthalten"
        # Optional: Prüfen, ob 'file_type' und 'icon' auch dabei sind
        assert "file_type" in overview, "Overview sollte 'file_type' enthalten"
        assert "icon" in overview, "Overview sollte 'icon' enthalten"


if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    test_load_paris_tour()

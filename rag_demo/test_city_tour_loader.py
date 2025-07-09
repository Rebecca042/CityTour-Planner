# test_city_tour_loader.py
from city_tour_loader import CityTourLoader

def test_load_paris_tour():
    folder_path = "docs/paris"  # Pfad zu den Dummy-Dateien für Paris
    loader = CityTourLoader(folder_path)
    overviews = loader.load_all_overviews()

    print(f"\nÜbersichten für Tour in {folder_path}:\n")
    for overview in overviews:
        print(overview)
        print("-" * 40)

if __name__ == "__main__":
    test_load_paris_tour()

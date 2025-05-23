from shapely.geometry import Point

from .sights import Sight  #p


def quiz_sight_modification(sight):
    print(f"\nCurrent information for {sight.name}:")
    print(f"Category: {sight.category}, Location: {sight.location}")

    # Ask for modifications
    sight.weather_suitability = input("Enter weather suitability (sunny/rainy/indoor/outdoor): ").strip()
    sight.description = input("Enter a description for this sight: ").strip()

    print(f"\nSight updated successfully! New details:")
    print(sight)

def quiz_add_sight():
    print("\n--- Add New Sight ---")
    name = input("Enter the name of the new sight: ").strip()
    lat = float(input("Enter latitude (e.g., 48.8566 for Paris): ").strip())
    lon = float(input("Enter longitude (e.g., 2.3522 for Paris): ").strip())
    category = input("Enter the category (e.g., café, museum, park): ").strip()

    # Create the sight and return it
    location = Point(lon, lat)
    sight = Sight(name, location, category)

    # Optionally, ask for further details using the modification function
    quiz_sight_modification(sight)

    return sight

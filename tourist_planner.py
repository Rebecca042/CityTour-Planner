import argparse
from datetime import date
from typing import Optional

from planner.data_loader import load_sights_from_csv, save_sights_to_csv
from planner.osm import fetch_osm_sights
from planner.get_route import plot_route_with_sights, plot_full_day_tour
from planner.base_planner import DayPlanner
from planner.weather import get_weather_forecast
from planner.userquiz import quiz_add_sight, quiz_sight_modification
from planner.display import show_cli_plan
from planner.genai import narrate
import unicodedata
from pathlib import Path
from slugify import slugify
from shapely.geometry import Point # Import Point
import osmnx as ox

def city_slug(city: str) -> str:
    """Convert 'Berlin, Germany' -> 'berlin'."""
    first_part = city.split(",")[0].strip().lower()
    # Fallback if slugify is outdated:
    # slug = re.sub(r"[^\w]+", "_", city.lower()).strip("_")
    # return slug
    return slugify(first_part)

def normalize(text):
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKD", text).casefold()

def export_csv_path(city: str) -> Path:
    # Keeps your “authoritative” CSVs untouched,
    # always exports as tourist_planner_sights_<slug>.csv
    slug = city_slug(city)
    return Path(f"tourist_planner_city_{slug}.csv")

def resolve_csv_path(city: str, cli_path: Optional[str]) -> Path:
    """
    Decide which CSV file to load:
    1. --sight-file CLI path (if given)
    2. city-specific file  data/sights_<city>.csv   (if it exists)
    3. generic fallback    data/sights.csv
    """
    if cli_path:
        return Path(cli_path)

    slug = city_slug(city)
    print(f"City slug is: {slug}")
    city_file = DEFAULT_DATA_DIR / f"sights_{slug}.csv"
    if city_file.is_file():
        return city_file

    return DEFAULT_DATA_DIR / "sights.csv"

CITY_CENTER_DEFAULT_COORDS = { # Use a lookup for defaults, similar to API/Streamlit
    "Paris": (48.8566, 2.3522),
    "Berlin": (52.52, 13.405),
}
# Define a central get_city_center function that returns Point
def get_city_center(city_name: str) -> Point:
    city_name = city_name.split(",")[0].strip() # Use only the city name for lookup
    if city_name in CITY_CENTER_DEFAULT_COORDS:
        lat, lon = CITY_CENTER_DEFAULT_COORDS[city_name]
    else:
        # Fallback to geocoding if not in lookup
        # You'll need to install osmnx (pip install osmnx) if not already
        print(f"Geocoding '{city_name}' using OpenStreetMap...")
        try:
            lat, lon = ox.geocode(city_name)
            CITY_CENTER_DEFAULT_COORDS[city_name] = (lat, lon) # Cache for future runs
        except Exception as e:
            print(f"Error geocoding city: {e}. Defaulting to Paris.")
            lat, lon = CITY_CENTER_DEFAULT_COORDS["Paris"]

    return Point(lon, lat) # Return Point(longitude, latitude)

DEFAULT_DATA_DIR = Path("data")
CSV_PATH = DEFAULT_DATA_DIR / "sights.csv"
MODES = ["walking", "cycling", "driving"]

def main():
    # Parse CLI args
    ap = argparse.ArgumentParser(description="Tour-planner CLI")
    ap.add_argument("--city", default="Paris, France", help="Place name for OpenStreetMap POI search")
    ap.add_argument("--use-osm", action="store_true", help="Load sights from OpenStreetMap instead of CSV")
    ap.add_argument("--refresh-osm", action="store_true", help="Force re-download of OSM data (ignore cache)")
    ap.add_argument("--sight-file", default=None, help="Path to CSV file with predefined sights")
    args = ap.parse_args()

    CITY_CENTER_POINT = get_city_center(args.city)
    print(f"Using city center: {CITY_CENTER_POINT.x}, {CITY_CENTER_POINT.y}")

    CSV_PATH = resolve_csv_path(args.city, args.sight_file)
    print(f"📁 Loading sights from: {CSV_PATH}")

    # Load sights
    if args.use_osm:
        TAGS = {
            "amenity": ["museum", "cafe", "restaurant"],
            "tourism": ["attraction", "gallery", "viewpoint"]
        }
        sights = fetch_osm_sights(args.city, TAGS, refresh=args.refresh_osm)
        if not sights:
            print("⚠️  No sights found via OSM, falling back to CSV.")
            sights = load_sights_from_csv(CSV_PATH)
    else:
        sights = load_sights_from_csv(CSV_PATH)


    clean_sights = []
    for s in sights:
        if isinstance(s.name, str):
            clean_sights.append(s)
        else:
            print(f"⚠️ Dropping malformed sight: {s} (name={s.name}, type={type(s.name)})")
    sights = clean_sights

    print(f"Loaded {len(sights)} sights")

    forecast = get_weather_forecast(CITY_CENTER_POINT, date.today())
    print(f"Weather forecast: {forecast}")

    selected_sights = []
    tour_sights = []

    planner = DayPlanner()

    while True:
        print("\nMenu: (1) View sights  (2) Add sight  (3) Modify sight  (4) Plan day  (5) Save & exit  (6) Select sights")
        choice = input("Select: ").strip()

        if choice == "1":
            for s in sights:
                print(s)

        elif choice == "2":
            new_sight = quiz_add_sight()
            sights.append(new_sight)

        elif choice == "3":
            name = input("Sight name to modify: ").strip()
            match = next((s for s in sights if normalize(s.name) == normalize(name)), None)
            if match:
                quiz_sight_modification(match)
            else:
                print("Not found.")

        elif choice == "6":
            print("Select sights for your tour by entering their names separated by commas:")
            names_input = input("Sight names: ").strip()
            names = [n.strip().lower() for n in names_input.split(",")]

            selected_sights = []
            for name in names:
                match = next((s for s in sights if normalize(s.name) == normalize(name)), None)
                if match:
                    selected_sights.append(match)
                else:
                    print(f"Sight '{name}' not found and will be skipped.")

            print(f"Selected {len(selected_sights)} sights for the tour.")

        elif choice == "4":
            print("Choose transport mode (walking/cycling/driving):")
            mode = input("Mode: ").strip().lower()
            if mode not in MODES:
                print(f"Invalid mode selected. Defaulting to walking.")
                mode = "walking"

            tour_sights_candidate = selected_sights if selected_sights else sights
            # Limit the number of sights to a maximum of 10
            tour_sights = tour_sights_candidate[:10]


            plan, weather, postcards, tour_plan = planner.plan_all(tour_sights, CITY_CENTER_POINT, mode, forecast)

            slot_postcards: dict[str, str] = {}
            idx = 0
            for slot, slot_sights in tour_plan.items():

                if postcards is not None:  # Check if it's not None first
                    if idx < len(postcards):
                        slot_postcards[slot] = postcards[idx]
                        idx += 1
                else:
                    # Handle the case where postcards is None, perhaps log a message or assign an empty list
                    postcards = []  # Assign an empty list to avoid future errors if needed
                    print("Warning: 'postcards' variable was None, treated as empty list.")

            from planner.display import show_cli_plan
            show_cli_plan(
                tour_plan=tour_plan,
                forecast=forecast,
                postcards=slot_postcards
            )
            #tour_sights = [s for slot_sights in tour_plan.values() for s in slot_sights]
            fmap = plot_full_day_tour(tour_plan, CITY_CENTER_POINT, mode=mode)
            map_file = "tourist_planner_sights_map.html"
            fmap.save(map_file)
            print(f"Interactive map saved to {map_file}")

            if tour_sights:
                narrate_choice = input(
                    "Would you like to generate LLM narrations for each time slot? (y/n): ").strip().lower()
                if narrate_choice == "y":
                    print("\n--- LLM Narrations ---")
                    for slot, sights in tour_plan.items():
                        sight_names = [s.name for s in sights]
                        narration = narrate(slot, args.city, sight_names, use_template=False)
                        print(f"\n🗓️ {slot.title()} narration:")
                        print(narration)

            print(f"Interactive map saved to {map_file}")

        elif choice == "5":
            export_path = export_csv_path(args.city)
            save_sights_to_csv(tour_sights, export_path)
            print("Data saved. Goodbye!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

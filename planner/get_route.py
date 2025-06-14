import time

import folium
from typing import List, Dict, Any, Tuple, Optional

import requests

from .net import get_with_backoff    #p

from typing import Union
from shapely.geometry import Point
from .sights import Sight # p
from .tour_planner_orchestrator import haversine
ICON_MAP = {
    "Cafe": {"icon": "coffee", "prefix": "fa", "color": "darkgreen"},
    "Restaurant": {"icon": "cutlery", "prefix": "fa", "color": "darkpurple"},
    "Museum": {"icon": "university", "prefix": "fa", "color": "darkblue"},
    "Park": {"icon": "tree", "prefix": "fa", "color": "green"},
    "Landmark": {"icon": "flag", "prefix": "fa", "color": "orange"},
    "Historic Site": {"icon": "building", "prefix": "fa", "color": "red"},
    "Shopping": {"icon": "shopping-cart", "prefix": "fa", "color": "cadetblue"},
    # Add more categories as needed, and choose appropriate icons/colors
    # Default icon if category not in map:
    #"default": {"icon": "info-sign", "prefix": "glyphicon", "color": "blue"}
    "default": {"icon": "star", "prefix": "fa", "color": "gray"}
}

# Define a mapping for OSRM profiles
OSRM_PROFILE_MAP = {
    "walking": "foot",
    "cycling": "bike",
    "driving": "car"
}


# get_route_details (used by original get_total_tour_length)
# This is the helper for the original get_total_tour_length,
# making individual OSRM calls per segment.
# It's kept as is to maintain compatibility with the original get_total_tour_length.
def get_route_details(start_location: Point, end_location: Point, mode: str = "walking") -> Optional[Dict[str, Any]]:
    """
    Fetches route details (distance and duration) between two points using the OSRM API.
    Used by the original get_total_tour_length for segment-by-segment calculation.
    """
    if not isinstance(start_location, Point) or not isinstance(end_location, Point):
        print(f"Error: Invalid Point objects for routing: start={start_location}, end={end_location}")
        return None

    coordinates = f"{start_location.x},{start_location.y};{end_location.x},{end_location.y}"
    profile = OSRM_PROFILE_MAP.get(mode, "foot")
    base = f"http://router.project-osrm.org/route/v1/{profile}/"
    url = f"{base}{coordinates}?overview=false&alternatives=false&steps=false"

    try:
        data = get_with_backoff(url)
        if data.get("code") != "Ok" or not data.get("routes"):
            # print(f"OSRM did not return a valid route for {start_location} to {end_location} ({mode}). Response: {data}")
            return None
        route = data["routes"][0]
        distance = route.get("distance")
        duration = route.get("duration")
        return {"distance": distance, "duration": duration}
    except Exception as e:
        print(f"Warning: Could not get route details from {start_location} to {end_location}: {e}")
        return None

def get_with_backoff(url: str, max_retries: int = 5, initial_delay: float = 1.0) -> Dict[str, Any]:
    """
    Fetches data from a URL with exponential backoff for retries.
    """
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                delay = initial_delay * (2 ** i)
                print(f"Request failed: {e}. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                raise # Re-raise the last exception if all retries fail
    return {} # Should not be reached, but for type hinting

def add_sight_markers(fmap: folium.Map, sights: List[Sight], color: str = "blue") -> None:
    """
    Adds markers for a list of Sight objects to an existing folium map.
    Markers use specific icons based on sight category, falling back to a default.
    The 'color' argument to this function is used for the icon's base color.
    """
    for s in sights:
        if isinstance(s.location, Point):
            # Get icon settings based on sight category
            print(f"DEBUG: Sight category: '{s.category}'") # Add this line
            # Convert the sight's category to Title Case (e.g., 'cafe' -> 'Cafe')
            standardized_category = s.category.title()
            print(f"DEBUG: Sight category: '{s.category}'")  # Add this line

            icon_settings = ICON_MAP.get(standardized_category, ICON_MAP["default"])
            print(f"DEBUG: Icon settings chosen: {icon_settings}")

            # Use the color passed to add_sight_markers for the icon's background color
            # Or you could use icon_settings["color"] if you want category-specific background colors
            marker_icon = folium.Icon(
                icon=icon_settings["icon"],
                prefix=icon_settings["prefix"],
                color=color # This uses the time-slot color (morning/afternoon/evening) for the icon's background
                # Or use icon_settings["color"] if you want category-specific background colors
            )

            folium.Marker(
                location=(s.location.y, s.location.x), # Folium expects (lat, lon)
                popup=f"<b>{s.name}</b> ({s.category})", # Added bold for clarity in popup
                icon=marker_icon
            ).add_to(fmap)


def get_osrm_route(coords: List[Tuple[float, float]], mode: str = "walking") -> Union[dict, None]:
    """
    Return a GeoJSON *feature* for the route (or None if <2 coords).
    Includes distance and duration in properties.
    """
    if len(coords) < 2:
        return None

    profile = OSRM_PROFILE_MAP.get(mode, "foot")
    base = f"http://router.project-osrm.org/route/v1/{profile}/"

    coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
    url = f"{base}{coord_str}?overview=full&geometries=geojson"

    data = get_with_backoff(url)

    # DEBUG LINE (keep for now, or remove if you're confident)
    # print(f"DEBUG: OSRM data for {coords}: {data}")

    if data.get("code") != "Ok" or not data.get("routes"):
        # We previously had `raise RuntimeError("OSRM returned no route")` here,
        # but returning None is more graceful for handling tour segments
        # that might not have a route (e.g., single sight, unroutable areas).
        return None

    route = data["routes"][0]  # Get the first (best) route
    route_coords = route["geometry"]["coordinates"]

    # --- IMPORTANT FIX: Extract distance and duration ---
    distance = route.get("distance", 0.0)
    duration = route.get("duration", 0.0)

    # return the geojson feature with populated properties
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": route_coords},
        "properties": {
            "distance": distance,
            "duration": duration
        },
    }



def add_route_and_markers_to_map(
    fmap: folium.Map,
    sights: List[Sight],
    color: str = "blue",
    mode: str = "walking"
) -> None:
    """
    Add markers and a colored route for a list of sights to an existing folium map.
    """
    if not sights:
        return  # nothing to add

    add_sight_markers(fmap, sights, color=color) # This will now apply category-specific icons

    # 1️⃣ build coordinate list once
    coords = [(s.location.x, s.location.y) for s in sights if isinstance(s.location, Point)]

    # 2️⃣ call routing helper (may return None)
    route_feature = get_osrm_route(coords, mode=mode)

    # 3️⃣ only draw a line if we actually have one
    if route_feature:
        geometry = route_feature["geometry"]
        latlon = [(lat, lon) for lon, lat in geometry["coordinates"]]
        folium.PolyLine(latlon, color=color, weight=5, opacity=0.8).add_to(fmap)


def plot_full_day_tour(tour_plan: Dict[str, List[Sight]], city_center: Point, mode: str = "walking") -> folium.Map: # Add mode here    # city_center is a shapely Point object
    # city_center is a shapely Point object
    city_center_latlon = (city_center.y, city_center.x)
    fmap = folium.Map(location=city_center_latlon, zoom_start=14)

    colors = {
        "morning": "blue",
        "afternoon": "green",
        "evening": "red"
    }

    for slot, sights in tour_plan.items():
        add_route_and_markers_to_map(fmap, sights, color=colors.get(slot, "blue"), mode=mode)

    return fmap

def plot_route_with_sights(sights: List[Sight], city_center: Point, mode: str = "walking", route_color: str = "blue") -> folium.Map:
    def create_map(center: Point, sights: List[Sight], zoom: int = 14) -> folium.Map:
        """
        Creates a Folium map centered on the city_center with sights marked.
        center is expected to be a shapely.geometry.Point.
        """
        # Convert the shapely.geometry.Point to a (latitude, longitude) tuple for Folium
        folium_center_coords = (center.y, center.x)  # Shapely Point: .y=lat, .x=lon

        fmap = folium.Map(location=folium_center_coords, zoom_start=zoom)
        if sights:
            latitudes = [s.location.y for s in sights if isinstance(s.location, Point)]
            longitudes = [s.location.x for s in sights if isinstance(s.location, Point)]
            if latitudes and longitudes:  # Only fit bounds if we have valid coordinates
                bounds = [[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]]
                fmap.fit_bounds(bounds)
        return fmap

    def add_route(fmap: folium.Map, route_geojson: Dict[str, Any], color: str) -> None:
        # Corrected: use route_geojson inside the function
        if "geometry" in route_geojson:
            coords = route_geojson["geometry"]["coordinates"]
        else:
            coords = route_geojson["coordinates"]

        # Convert to (lat, lon) for PolyLine (folium wants lat/lon)
        latlon_coords = [(lat, lon) for lon, lat in coords]
        folium.PolyLine(latlon_coords, color=color, weight=5, opacity=0.8).add_to(fmap)

    coords_for_osrm = [(s.location.x, s.location.y) for s in sights if isinstance(s.location, Point)]
    route = get_osrm_route(coords_for_osrm, mode=mode)

    fmap = create_map(city_center, sights)

    add_sight_markers(fmap, sights)
    add_route(fmap, route, route_color)

    return fmap


async def generate_information_full_day_tour(
        tour_plan: Dict[str, List[Sight]],
        city_center: Point,
        mode: str = "walking"
) -> Dict[str, Any]:
    """
    Generates comprehensive information for a full-day tour plan,
    including the total tour length and estimated duration using a single, efficient
    OSRM call for the entire aggregated route.
    Additionally, it calculates and returns the lengths of individual subtours
    (within each time slot) and their sum.

    Args:
        tour_plan (dict): A dictionary where keys are time slots (e.g., "morning")
                          and values are lists of Sight objects.
        city_center (Point): The central point of the city for routing.
        mode (str): The travel mode (e.g., "walking").

    Returns:
        Dict[str, Any]: A dictionary containing:
                        - 'total_length_meters': Total length of the *entire* day's travel (including returns to center).
                        - 'total_duration_seconds': Estimated total duration of the *entire* day's travel.
                        - 'full_route_geojson': GeoJSON feature for the entire tour route.
                        - 'message': A status message.
                        - 'subtour_lengths_meters': Dict of lengths for 'morning', 'afternoon', 'evening' segments (only within sights).
                        - 'subtour_durations_seconds': Dict of durations for 'morning', 'afternoon', 'evening' segments (only within sights).
                        - 'total_subtour_length_meters': Sum of lengths of all subtours (morning, afternoon, evening).
    """
    ordered_slots = ["morning", "afternoon", "evening"]

    # Initialize results for the overall tour
    total_length_meters = 0.0
    total_duration_seconds = 0.0
    full_route_geojson_coords = [] # To build the full day's route coordinates
    message = "Tour information generated successfully."

    # Initialize results for individual subtours
    subtour_lengths_meters = {slot: 0.0 for slot in ordered_slots}
    subtour_durations_seconds = {slot: 0.0 for slot in ordered_slots}

    haversine_total_length_meters = 0.0
    haversine_subtour_lengths_meters = {slot: 0.0 for slot in ordered_slots}
    haversine_total_subtour_length_meters = 0.0

    # --- Calculate total tour length (including travel to/from center and between slots) ---
    # This part remains largely as your original, making one OSRM call for the full path.
    all_tour_points: List[Point] = []
    all_tour_points.append(city_center) # Start from city center

    for slot in ordered_slots:
        sights_in_slot = tour_plan.get(slot, [])
        for sight in sights_in_slot:
            if sight.location:
                all_tour_points.append(sight.location)

    if len(all_tour_points) > 1: # Only add return if there was at least one sight after city_center
        all_tour_points.append(city_center) # Return to city center

    coords_for_osrm_full_tour = [(p.x, p.y) for p in all_tour_points]

    if len(coords_for_osrm_full_tour) >= 2:
        full_tour_route_info = get_osrm_route(coords_for_osrm_full_tour, mode=mode)
        if full_tour_route_info:
            total_length_meters = full_tour_route_info['properties'].get("distance", 0.0)
            total_duration_seconds = full_tour_route_info['properties'].get("duration", 0.0)
            full_route_geojson = full_tour_route_info # The full route GeoJSON feature
        else:
            message = f"OSRM returned no route for the full tour. Check logs."
    else:
        message = "Not enough points to generate a full tour route (need at least 2 unique points)."

    total_subtour_length_meters = 0.0
    # --- Calculate individual subtour lengths and total subtour length ---
    for slot in ordered_slots:
        sights_in_slot = tour_plan.get(slot, [])
        slot_points = [s.location for s in sights_in_slot if s.location]

        if len(slot_points) >= 2: # Need at least 2 points for a route within the slot
            coords_for_osrm_subtour = [(p.x, p.y) for p in slot_points]
            print(
                f"DEBUG: Calling get_osrm_route with coords: {coords_for_osrm_subtour}, mode: {mode}")  # Add this line
            slot_route_info = get_osrm_route(coords_for_osrm_subtour, mode=mode) # Pass the converted list
            if slot_route_info:
                current_slot_length = slot_route_info['properties'].get("distance", 0.0)
                print(f"DEBUG: Length for slot {slot}: {current_slot_length}")  # Add this line
            else:
                current_slot_length = 0.0
            if slot_route_info:
                current_slot_length = slot_route_info['properties'].get("distance", 0.0)
                current_slot_duration = slot_route_info['properties'].get("duration", 0.0)
            else:
                print(f"Warning: OSRM returned no route for {slot} subtour.")
                current_slot_length = 0.0
                current_slot_duration = 0.0
        elif len(slot_points) == 1: # A single sight has 0 internal travel length
            current_slot_length = 0.0
            current_slot_duration = 0.0
        else: # No valid points in slot
            current_slot_length = 0.0
            current_slot_duration = 0.0
            print(f"Info: No valid sights with locations found for {slot} slot. Subtour length is 0.")

        subtour_lengths_meters[slot] = current_slot_length
        subtour_durations_seconds[slot] = current_slot_duration
        total_subtour_length_meters += current_slot_length

    # --- NEW: Calculate Haversine Distances ---
    # 1. Total Haversine Distance (City Center -> All Sights -> City Center)
    # This directly uses the all_tour_points list prepared for OSRM.
    current_haversine_segment_start = None
    for i, p in enumerate(all_tour_points):
        if i == 0:
            current_haversine_segment_start = p
            continue

        if current_haversine_segment_start and p:
            haversine_total_length_meters += haversine(current_haversine_segment_start, p)
        current_haversine_segment_start = p

    # 2. Haversine Distances for Individual Subtours
    for slot in ordered_slots:
        sights_in_slot = tour_plan.get(slot, [])
        slot_points_shapely = [s.location for s in sights_in_slot if s.location]

        current_slot_haversine_length = 0.0
        if len(slot_points_shapely) >= 2:
            # Calculate haversine for segments within the slot
            haversine_segment_start = None
            for i, p in enumerate(slot_points_shapely):
                if i == 0:
                    haversine_segment_start = p
                    continue
                if haversine_segment_start and p:
                    current_slot_haversine_length += haversine(haversine_segment_start, p)
                haversine_segment_start = p
        elif len(slot_points_shapely) == 1:
            # A single sight has 0 internal travel length
            current_slot_haversine_length = 0.0
        # If len is 0, it stays 0.0 initialized

        haversine_subtour_lengths_meters[slot] = current_slot_haversine_length
        haversine_total_subtour_length_meters += current_slot_haversine_length

    # --- Return Results ---
    return {
        'total_length_meters': total_length_meters,
        'total_duration_seconds': total_duration_seconds,
        'full_route_geojson': full_route_geojson,
        'message': message,
        'subtour_lengths_meters': subtour_lengths_meters,
        'subtour_durations_seconds': subtour_durations_seconds,
        'total_subtour_length_meters': total_subtour_length_meters,
        # --- NEW HAVERSINE METRICS ---
        'haversine_total_length_meters': haversine_total_length_meters,
        'haversine_subtour_lengths_meters': haversine_subtour_lengths_meters,
        'haversine_total_subtour_length_meters': haversine_total_subtour_length_meters
    }


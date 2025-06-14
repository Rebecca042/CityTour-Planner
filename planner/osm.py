from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
import math
import osmnx as ox
import pandas as pd
from shapely.geometry import Point
from .sights import Sight   #p @dataclass(frozen=True)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# Helper function to generate a cache file path based on a query identifier.
# This identifier can be a city name or a string representation of coordinates and radius.
def _cache_path(query_identifier: str) -> Path:
    """
    Generates a safe filename for caching based on a query identifier.
    Converts the identifier into a URL-friendly slug.
    """
    # Replace common characters that might cause issues in filenames
    slug = query_identifier.lower().replace(" ", "_").replace(",", "").replace("(", "").replace(")", "").replace(".", "_").replace("-", "_").replace("/", "_")
    # Limit slug length to avoid excessively long filenames, while maintaining uniqueness
    if len(slug) > 100:
        import hashlib
        slug = hashlib.sha256(query_identifier.encode()).hexdigest()[:100] # Use a hash if too long
    return CACHE_DIR / f"pois_{slug}.json"

# Helper function to safely convert a value to a string, handling None and NaN.
def safe_str(val) -> str:
    """
    Converts a value to a string safely, returning "unknown" for None or NaN.
    """
    if val is None:
        return "unknown"
    if isinstance(val, float) and math.isnan(val):
        return "unknown"
    return str(val)

# Example assign_weather_suitability based on category
def assign_weather_suitability(category: str) -> tuple[str, ...]:
    category = safe_str(category).lower()
    if category in ("park", "garden", "leisure_park"):
        return ("sunny",)
    elif category in ("museum", "gallery", "arts_centre", "art", "theatre", "place_of_worship", "school"):
        return ("rainy", "any")
    elif category in ("fountain", "bench", "clock", "viewpoint"):
        return ("sunny", "cloudy")
    elif category in ("bar", "restaurant", "cafe"):
        return ("any",)  # Indoor/outdoor mixed
    # Add more categories and preferences as needed
    return ("any",)

def fetch_osm_sights(
    location: Union[str, Point], # Can now be a string (city name) or a shapely Point (lon, lat)
    tags: Dict[str, List[str]],
    refresh: bool = True, # Refresh needed for coords - option
    radius_meters: Optional[int] = 1000 # New optional parameter for radius
) -> List[Sight]:
    """
    Fetches points of interest (sights) using OSMnx, either from a place name or around a central point.
    Results are cached to JSON files.

    Args:
        location (Union[str, Point]): A city name (str) or a shapely Point object (lon, lat).
        tags (Dict[str, List[str]]): OSM tags to query for (e.g., {"amenity": ["restaurant", "cafe"]}).
        refresh (bool): Whether to clear the OSMnx cache and refetch data, bypassing local JSON cache.
        radius_meters (Optional[int]): Radius in meters to query around the point if 'location' is a Point.
                                       Required if location is a Point.

    Returns:
        List[Sight]: A list of Sight objects.
    """
    # Determine the query identifier for caching
    query_identifier: str
    if isinstance(location, str):
        query_identifier = location
    elif isinstance(location, Point):
        if radius_meters is None:
            raise ValueError("radius_meters must be provided when 'location' is a shapely.geometry.Point.")
        # Create a unique identifier for point-based queries (latitude, longitude, radius)
        query_identifier = f"point_{location.y:.6f}_{location.x:.6f}_radius_{radius_meters}"
    else:
        raise ValueError("Location must be a string (city name) or a shapely.geometry.Point.")


    cache_file = _cache_path(query_identifier)

    # If refresh is False and cache file exists, load from cache
    if cache_file.exists() and not refresh:
        try:
            with cache_file.open() as f:
                raw_data = json.load(f)
            # Deserialize cached data into Sight objects
            return [
                Sight(
                    #id=rec.get("id"),  # Include id from cache
                    name=rec["name"],
                    location=Point(rec["lon"], rec["lat"]),  # Reconstruct Point (lon, lat)
                    category=rec["category"],
                    weather_suitability=tuple(rec["weather_suitability"]),
                    description=rec.get("description", "")
                )
                for rec in raw_data
            ]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading cache file {cache_file}: {e}. Will refetch data.")
            # If cache is corrupted or malformed, proceed to refetch
            pass

    # --- Query OSMnx ----------------------------------------------------------------
    # Clear OSMnx cache if refresh is True. This clears OSMnx's internal cache, not our JSON cache.
    if refresh:
        ox.settings.log_console = True
        try:
            # Attempt the most current method first
            ox.downloader.clear_cache(ox.settings.cache_folder, response=True, parsed=True)
        except AttributeError:
            try:
                # Fallback to a previous common method
                ox.utils_geo.clear_cache(ox.settings.cache_folder, response=True, parsed=True)
            except AttributeError:
                try:
                    # Fallback to an even older method (less likely to work if previous failed)
                    ox.utils.clear_cache(ox.settings.cache_folder, response=True, parsed=True)
                except AttributeError:
                    print("Warning: Could not find a suitable OSMnx cache clearing function. "
                          "Please ensure your OSMnx version is up-to-date or check its documentation "
                          "for the correct cache clearing method.")
                    # If all attempts fail, we proceed without clearing OSMnx's internal cache,
                    # but our JSON cache will still be bypassed due to `refresh=True`.

    gdf = pd.DataFrame()  # Initialize empty GeoDataFrame

    if isinstance(location, str):
        # Logic for city names (place-based query)
        try:
            gdf = ox.features.features_from_place(location, tags=tags)
        except Exception as e:
            print(f"Error fetching features for place '{location}': {e}")
            return []
    elif isinstance(location, Point):
        # Logic for coordinates (point-based query)
        # osmnx.features.features_from_point expects (latitude, longitude)
        # Shapely Point stores (longitude, latitude), so extract correctly
        lat, lon = location.y, location.x
        try:
            gdf = ox.features.features_from_point((lat, lon), tags=tags, dist=radius_meters)
        except Exception as e:
            print(f"Error fetching features around point ({lat}, {lon}) with radius {radius_meters}m: {e}")
            return []

    sights: List[Sight] = []
    if not gdf.empty:
        # Convert GeoDataFrame to list of Sight objects
        for _, row in gdf.iterrows():
            name = row.get('name')
            if not name:
                continue  # Skip sights without a name

            # Robust category determination based on requested tags
            category = 'Unknown'
            for tag_key, tag_values in tags.items():
                if tag_key in row:
                    row_value = row[tag_key]

                    # Case 1: tag_values is True (meaning match any value for this tag_key)
                    if tag_values is True:
                        # If row_value is a list, pick the first non-empty string item
                        if isinstance(row_value, list):
                            for item in row_value:
                                if item is not None and str(item).strip() != '':
                                    category = str(item)
                                    break
                            if category != 'Unknown':
                                break  # Found category, break outer loop
                        # If row_value is a single value, use it directly
                        else:
                            if row_value is not None and str(row_value).strip() != '':
                                category = str(row_value)
                                break  # Found category, break outer loop
                    # Case 2: tag_values is a list of strings (standard behavior)
                    elif isinstance(tag_values, list):
                        # If row_value is a list, iterate through its items
                        if isinstance(row_value, list):
                            for item in row_value:
                                # Convert each item to string for comparison against tag_values
                                if str(item) in tag_values:
                                    category = str(item)
                                    break  # Found a category in the list, break inner loop
                            if category != 'Unknown':  # If a category was found in the list, break outer loop
                                break
                        # If row_value is a single value (string, bool, int, float, etc.)
                        else:
                            # Convert the single value to string for comparison against tag_values
                            if str(row_value) in tag_values:
                                category = str(row_value)
                                break  # Found a category, break outer loop
                    # Else (tag_values is neither True nor a list), it's an unexpected type for tags.items().
                    # We will simply skip this tag_key as it doesn't fit our expected patterns.

            # Use centroid for location (robust for both Points and Polygons)
            latitude = row.geometry.centroid.y if row.geometry else None
            longitude = row.geometry.centroid.x if row.geometry else None

            if latitude is not None and longitude is not None:
                sights.append(
                    Sight(
                        #id=row.get('osm_id'),  # Use osm_id as unique ID for the Sight
                        name=name,
                        location=Point(longitude, latitude),  # Store as Shapely Point (lon, lat)
                        category=category,
                        weather_suitability=assign_weather_suitability(category),
                        description=row.get("description", "")
                    )
                )
    else:
        print(f"No OSM features found for query. Location: {location} (type: {type(location).__name__}), Tags: {tags}, Radius: {radius_meters}m. GeoDataFrame is empty.")


    # Cache the fetched data
    serial_data = [
        {
            #"id": s.id,  # Include ID in cached data
            "name": s.name,
            "lon": s.location.x,  # Store longitude
            "lat": s.location.y,  # Store latitude
            "category": s.category,
            "weather_suitability": list(s.weather_suitability),
            "description": s.description,
        }
        for s in sights
    ]
    try:
        with cache_file.open("w") as f:
            json.dump(serial_data, f, indent=2)
    except IOError as e:
        print(f"Error writing to cache file {cache_file}: {e}")

    return sights
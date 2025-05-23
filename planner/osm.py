from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict
import math
import osmnx as ox
from shapely.geometry import Point
from .sights import Sight   #p @dataclass(frozen=True)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# helper -------------------------------------------------------------
def _cache_path(city: str) -> Path:
    slug = city.lower().replace(" ", "_").replace(",", "")
    return CACHE_DIR / f"pois_{slug}.json"

# Add this helper function for safe string conversion
def safe_str(val) -> str:
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
    city: str,
    tags: Dict[str, List[str]],
    refresh: bool = False
) -> List[Sight]:
    """
    Query OpenStreetMap once and cache to JSON.
    Returns a list of models.Sight.
    """
    cache_file = _cache_path(city)
    if cache_file.exists() and not refresh:
        with cache_file.open() as f:
            raw = json.load(f)
        return [
            Sight(
                name=rec["name"],
                location=Point(rec["lon"], rec["lat"]),
                category=rec["category"],
                weather_suitability=tuple(rec["weather_suitability"]),
                description=rec.get("description", "")
            )
            for rec in raw
        ]

    # --- query OSMnx ----------------------------------------------------------------
    gdf = ox.features_from_place(city, tags=tags)

    sights: List[Sight] = []
    for _, row in gdf.iterrows():
        name = row.get("name")
        if not name or not hasattr(row.geometry, "centroid"):
            continue
        centroid = row.geometry.centroid

        # Safely get category string
        raw_category = row.get("amenity") or row.get("tourism") or "unknown"
        category = safe_str(raw_category)

        sights.append(
            Sight(
                name=name,
                location=Point(centroid.x, centroid.y),
                category=category,
                weather_suitability=assign_weather_suitability(category),
                description=row.get("description", "")
            )
        )

    # cache --------------------------------------------------------------------------
    serial = [
        {
            "name": s.name,
            "lon": s.location.x,
            "lat": s.location.y,
            "category": s.category,
            "weather_suitability": list(s.weather_suitability),
            "description": s.description,
        }
        for s in sights
    ]
    with cache_file.open("w") as f:
        json.dump(serial, f, indent=2)

    return sights

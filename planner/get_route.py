import requests

from typing import List, Dict, Any, Tuple, Union


from .net import get_with_backoff    #p

from typing import Union

def get_osrm_route(coords: List[Tuple[float, float]], mode: str = "walking") -> Union[dict, None]:

    """
    Return a GeoJSON *feature* for the route (or None if <2 coords).
    """
    # ---------- NEW GUARD CLAUSE -----------------------------------
    if len(coords) < 2:                       # nothing to route
        return None                           # >>> early-return

    base = "http://router.project-osrm.org/route/v1/foot/"
    coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
    url = f"{base}{coord_str}?overview=full&geometries=geojson"

    data = get_with_backoff(url)
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError("OSRM returned no route")

    route_coords = data["routes"][0]["geometry"]["coordinates"]

    # return the geojson
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": route_coords},
        "properties": {},
    }

import folium
import folium
from typing import List, Dict, Any, Tuple

def add_route_and_markers_to_map(
    fmap: folium.Map,
    sights: List[Any],
    color: str = "blue",
    mode: str = "walking"
) -> None:
    """
    Add markers and a colored route for a list of sights to an existing folium map.
    """
    if not sights:
        return  # nothing to add

    def add_sight_markers(fmap: folium.Map, sights: List[Any]) -> None:
        for s in sights:
            folium.Marker(
                location=(s.location.y, s.location.x),
                popup=f"{s.name} ({s.category})"
            ).add_to(fmap)

    #def add_route(fmap: folium.Map, route_geojson_feature: Dict[str, Any], color: str) -> None:
    #    # Extract the geometry from the feature
    #    geometry = route_geojson_feature.get("geometry")
    #    if not geometry or "coordinates" not in geometry:
    #        raise ValueError("Invalid GeoJSON Feature: missing geometry or coordinates")#

    #    coords = geometry["coordinates"]
    #    coords_latlon = [(lat, lon) for lon, lat in coords]
    #    folium.PolyLine(coords_latlon, color=color, weight=5, opacity=0.8).add_to(fmap)

    #coords = [(s.location.x, s.location.y) for s in sights]
    #route_feature = get_osrm_route(coords, mode=mode)

    #add_sight_markers(fmap, sights)
    #add_route(fmap, route_feature, color)'''
    # ---- (unchanged) add_sight_markers ----------------------------
    for s in sights:
        folium.Marker(
            location=(s.location.y, s.location.x),
            popup=f"{s.name} ({s.category})"
        ).add_to(fmap)

    # 1️⃣ build coordinate list once
    coords = [(s.location.x, s.location.y) for s in sights]

    # 2️⃣ call routing helper (may return None)
    route_feature = get_osrm_route(coords, mode=mode)

    # 3️⃣ only draw a line if we actually have one
    if route_feature:
        geometry = route_feature["geometry"]
        latlon = [(lat, lon) for lon, lat in geometry["coordinates"]]
        folium.PolyLine(latlon, color=color, weight=5, opacity=0.8).add_to(fmap)


def plot_full_day_tour(tour_plan: Dict[str, List[Any]], city_center: Any) -> folium.Map:
    # city_center is a shapely Point object
    city_center_latlon = (city_center.y, city_center.x)
    fmap = folium.Map(location=city_center_latlon, zoom_start=14)

    colors = {
        "morning": "blue",
        "afternoon": "green",
        "evening": "red"
    }

    for slot, sights in tour_plan.items():
        add_route_and_markers_to_map(fmap, sights, color=colors.get(slot, "blue"))

    return fmap

def plot_route_with_sights(sights: List[Any], city_center: Tuple[float, float], route_color: str = "blue") -> folium.Map:
    def create_map(center: Tuple[float, float], sights: List[Any], zoom: int = 14) -> folium.Map:
        fmap = folium.Map(location=center, zoom_start=zoom)
        if sights:
            latitudes = [s.location.y for s in sights]
            longitudes = [s.location.x for s in sights]
            bounds = [[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]]
            fmap.fit_bounds(bounds)
        return fmap

    def add_sight_markers(fmap: folium.Map, sights: List[Any]) -> None:
        for s in sights:
            folium.Marker(
                location=(s.location.y, s.location.x),
                popup=f"{s.name} ({s.category})"
            ).add_to(fmap)

    def add_route(fmap: folium.Map, route_geojson: Dict[str, Any], color: str) -> None:
        # Corrected: use route_geojson inside the function
        if "geometry" in route_geojson:
            coords = route_geojson["geometry"]["coordinates"]
        else:
            coords = route_geojson["coordinates"]

        # Convert to (lat, lon) for PolyLine (folium wants lat/lon)
        latlon_coords = [(lat, lon) for lon, lat in coords]
        folium.PolyLine(latlon_coords, color=color, weight=5, opacity=0.8).add_to(fmap)

    coords = [(s.location.x, s.location.y) for s in sights]
    route = get_osrm_route(coords, mode="walking")

    fmap = create_map(city_center, sights)
    add_sight_markers(fmap, sights)

    add_route(fmap, route, route_color)

    return fmap


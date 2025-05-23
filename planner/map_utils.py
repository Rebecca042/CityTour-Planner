# planner/map_utils.py

from typing import List
import folium
from shapely.geometry import Point
from .sights import Sight  #p


def generate_map(sights: List[Sight], center: Point, zoom_start: int = 14) -> folium.Map:
    """
    Generate a folium map centered at 'center' with markers for each sight.

    Parameters:
    - sights: List of Sight objects to plot
    - center: shapely Point with lon/lat coordinates
    - zoom_start: initial zoom level

    Returns:
    - folium.Map object
    """
    fmap = folium.Map(location=[center.y, center.x], zoom_start=zoom_start)

    for sight in sights:
        popup = f"<b>{sight.name}</b><br>Category: {sight.category}<br>Suitability: {', '.join(sight.weather_suitability)}"
        folium.Marker(
            location=[sight.location.y, sight.location.x],
            popup=popup,
            tooltip=sight.name
        ).add_to(fmap)

    return fmap


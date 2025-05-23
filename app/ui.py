# app/ui.py
from shapely.geometry import Point
import streamlit as st
import osmnx as ox

from typing import Optional

def get_user_city_input(city_coords_cache: dict) -> tuple[Optional[str], Optional[Point]]:

    """
    Display city input UI and return city name and center point.

    Args:
        city_coords_cache (dict): Cache of city name to (lat, lon) tuples.

    Returns:
        Tuple of city name (str or None) and shapely Point of city center (or None).
    """
    mode = st.radio("Choose input mode:", ["Select city", "Type city name", "Enter coordinates"])

    city = None
    city_center = None

    if mode == "Select city":
        city = st.selectbox("City:", sorted(city_coords_cache.keys()), key="select_city")
        if city:
            lat, lon = city_coords_cache[city]
            city_center = Point(lon, lat)

    elif mode == "Type city name":
        city = st.text_input("City name:", key="type_city")
        if city:
            if city in city_coords_cache:
                lat, lon = city_coords_cache[city]
            else:
                lat, lon = ox.geocode(city)
                city_coords_cache[city] = (lat, lon)
            city_center = Point(lon, lat)

    elif mode == "Enter coordinates":
        lat = st.number_input("Latitude", format="%.6f", key="lat")
        lon = st.number_input("Longitude", format="%.6f", key="lon")
        if lat != 0.0 and lon != 0.0:
            city_center = Point(lon, lat)
            city = f"Coords({lat:.6f}, {lon:.6f})"

    return city, city_center

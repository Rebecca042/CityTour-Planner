# frontend/ui.py
from shapely.geometry import Point
import streamlit as st
import osmnx as ox

from typing import Dict, Tuple, Optional


# Function to reverse geocode a point to a city name
@st.cache_data(show_spinner=False)  # Cache this function as it makes external API calls
def reverse_geocode_point_to_city(_point: Point) -> Optional[str]:
    """
    Attempts to reverse geocode a shapely Point to a human-readable city name.
    Uses OSMnx's geocoding capabilities.
    """
    try:
        # ox.geocode_point_to_address expects (latitude, longitude)
        # Shapely Point stores (longitude, latitude), so extract correctly
        address = ox.geocode_point_to_address((_point.y, _point.x), amenities=False, distance=10000)  # Search within 500m

        # The address string can be complex (e.g., "Eiffel Tower, 75007 Paris, France")
        # Try to extract a common city/town component. This is a heuristic.
        parts = [p.strip() for p in address.split(',')]

        # Common pattern: city is often the second to last part, or a named part
        if len(parts) >= 2:
            # Check if one of the parts looks like a city name (e.g., not a postal code)
            # This is a very basic heuristic, could be improved with more robust address parsing libraries
            potential_city = parts[-2]
            if not potential_city.isdigit() and len(potential_city) > 2:  # Simple check to avoid postal codes
                return potential_city

        # Fallback to the last part (often country or major region)
        return parts[-1] if parts else None

    except Exception as e:
        # print(f"DEBUG: Reverse geocoding failed for {point}: {e}") # For debugging
        return None

def get_user_city_input(city_coords_cache: Dict[str, Tuple[float, float]]) -> Tuple[Optional[str], Optional[Point]]:
    """
    Display city input UI and return city name and center point.
    Ensures consistent behavior with st.session_state, especially when switching
    between demo mode and manual selection.

    Args:
        city_coords_cache (dict): Cache of city name to (lat, lon) tuples.

    Returns:
        Tuple of city name (str or None) and shapely Point of city center (or None).
    """
    city: Optional[str] = None
    city_center: Optional[Point] = None

    # --- Initialize st.session_state.user_city if it doesn't exist ---
    # This ensures a default value even before any user interaction.
    if "user_city" not in st.session_state:
        st.session_state.user_city = "Berlin"  # Default to Berlin

    if st.session_state.get("demo_mode_active", False):
        # --- DEMO MODE ---
        # Demo mode always overrides user selection.
        demo_city_name = st.session_state.user_city  # Get the demo city from session state ("Paris, France")

        st.subheader("City Selection (Demo Mode Active)")
        st.info(f"City set to **{demo_city_name}** automatically for demo.")
        st.selectbox("City:", options=[demo_city_name], index=0, disabled=True, key="demo_city_display")

        city = demo_city_name

        # --- Fetch city center for the demo city ---
        if city:
            if city in city_coords_cache:
                lat, lon = city_coords_cache[city]
            else:
                try:
                    lat, lon = ox.geocode(city)
                    city_coords_cache[city] = (lat, lon)
                except Exception as e:
                    st.error(f"Could not find coordinates for demo city '{city}': {e}. Please check its name.")
                    city = None
            if city:
                city_center = Point(lon, lat)

    else:
        # --- MANUAL SELECTION ---
        # Use a single selectbox for both predefined and typed cities.  This is much cleaner.
        city_options = sorted(list(city_coords_cache.keys())) + ["Type a city name", "Enter coordinates"]

        # Determine the index to pre-select in the dropdown.  This is KEY.
        # If st.session_state.user_city is a predefined city, select it.
        # Otherwise, default to "Type a city name" or the first city.
        if st.session_state.user_city in city_coords_cache:
            default_index = city_options.index(st.session_state.user_city)
        elif st.session_state.user_city == "Type a city name" or st.session_state.user_city == "Enter coordinates":
            default_index = city_options.index(st.session_state.user_city)  # Keep the previous mode
        else:
            default_index = 0  # Default to the first city in the list

        selected_option = st.selectbox(
            "Select or type a city:",
            options=city_options,
            index=default_index,  # Use the calculated default
            key="city_selector"   # Unique key is essential
        )

        # Update st.session_state.user_city based on selection
        st.session_state.user_city = selected_option

        if selected_option in city_coords_cache:
            # Predefined city selected
            city = selected_option
            lat, lon = city_coords_cache[city]
            city_center = Point(lon, lat)
        elif selected_option == "Type a city name":
            city_input = st.text_input("City name:", key="typed_city_name")
            if city_input:
                city = city_input
                try:
                    lat, lon = ox.geocode(city)
                    city_coords_cache[city] = (lat, lon)
                    city_center = Point(lon, lat)
                except Exception as e:
                    st.error(f"Could not find coordinates for the entered city: {e}. Please try another.")
                    city = None
        elif selected_option == "Enter coordinates":
            lat = st.number_input("Latitude", format="%.6f", key="lat_input")
            lon = st.number_input("Longitude", format="%.6f", key="lon_input")
            radius = st.number_input("Search Radius (meters)", min_value=100, max_value=20000, value=5000, step=500, key="radius_input_coords")

            if lat != 0.0 and lon != 0.0:
                city_center = Point(lon, lat)
                st.session_state.radius_for_point_query = radius

                # Attempt to reverse geocode
                try:
                    location = (lat, lon) # Pass as tuple for reverse_geocode
                    city = ox.geocode_to_gdf(location).at[0, 'name'] # Extract city name
                    st.success(f"Detected city: **{city}**")
                except Exception:
                     city = f"Coords({lat:.6f}, {lon:.6f})"  # Fallback to "Coords(...)"
                     st.warning("Could not identify a city for these coordinates. Using raw coordinates.")

            else:
                city = None
                if "radius_for_point_query" in st.session_state:
                    del st.session_state.radius_for_point_query
                city_center = None

    return city, city_center

def get_user_city_input_old(city_coords_cache: dict) -> tuple[Optional[str], Optional[Point]]:

    """
    Display city input UI and return city name and center point.

    Args:
        city_coords_cache (dict): Cache of city name to (lat, lon) tuples.

    Returns:
        Tuple of city name (str or None) and shapely Point of city center (or None).
    """
    city: Optional[str] = None  # Initialize city to None
    city_center: Optional[Point] = None

    if st.session_state.get("demo_mode_active", False) and st.session_state.get("user_city"):
        # In demo mode, force the selection to the demo city
        demo_city_name = st.session_state.user_city

        st.subheader("City Selection (Demo Mode Active)")
        st.info(f"City set to **{demo_city_name}** automatically for demo.")
        st.selectbox("City:", options=[demo_city_name], index=0, disabled=True, key="demo_city_display")

        city = demo_city_name
        # Fetch city center for the demo city
        if city:
            if city in city_coords_cache:
                lat, lon = city_coords_cache[city]
            else:
                try:  # Try to geocode if not in cache (e.g., "Paris, France" is not in CITY_COORDS by default)
                    lat, lon = ox.geocode(city)
                    city_coords_cache[city] = (lat, lon)  # Add to cache for next time
                except Exception:
                    st.error(f"Could not find coordinates for demo city '{city}'. Please check its name.")
                    city = None  # Invalidate if geocoding fails
            if city:  # Only set city_center if city is valid
                city_center = Point(lon, lat)

    else:
        # --- ORIGINAL LOGIC FOR MANUAL SELECTION ---
        mode = st.radio("Choose input mode:", ["Select city", "Type city name", "Enter coordinates"],
                        key="input_mode_radio")

        if mode == "Select city":
            # Add a default blank option or ensure it starts with a valid city
            city_options = [""] + sorted(list(city_coords_cache.keys()))
            selected_city = st.selectbox("City:", city_options, key="select_city")
            if selected_city:
                city = selected_city
                lat, lon = city_coords_cache[city]
                city_center = Point(lon, lat)

        elif mode == "Type city name":
            city_input = st.text_input("City name:", key="type_city")
            if city_input:
                city = city_input
                try:
                    if city in city_coords_cache:
                        lat, lon = city_coords_cache[city]
                    else:
                        lat, lon = ox.geocode(city)
                        city_coords_cache[city] = (lat, lon)
                    city_center = Point(lon, lat)
                except Exception:
                    st.error("Could not find coordinates for the entered city. Please try another.")
                    city = None  # Invalidate city if coordinates can't be found

        elif mode == "Enter coordinates":
            lat = st.number_input("Latitude", format="%.6f", key="lat_input")
            lon = st.number_input("Longitude", format="%.6f", key="lon_input")
            radius = st.number_input("Search Radius (meters)", min_value=100, max_value=20000, value=5000, step=500, key="radius_input_coords")

            if lat != 0.0 and lon != 0.0:
                city_center = Point(lon, lat)  # This is the Point object
                st.session_state.radius_for_point_query = radius

                # Attempt to reverse geocode to get a human-readable city name
                reverse_geocoded_city = reverse_geocode_point_to_city(city_center)
                if reverse_geocoded_city:
                    city = reverse_geocoded_city
                    st.success(f"Detected city: **{city}**")
                else:
                    city = f"Coords({lat:.6f}, {lon:.6f})"  # Fallback to "Coords(...)" if no city found
                    st.warning("Could not identify a city for these coordinates. Using raw coordinates.")
            else:
                city = None  # Invalidate if coordinates are 0.0, 0.0
                if "radius_for_point_query" in st.session_state:
                    del st.session_state.radius_for_point_query
                city_center = None

    return city, city_center

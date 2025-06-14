import os
import streamlit as st
import requests
from streamlit_folium import st_folium
from frontend.ui import get_user_city_input
from typing import List, Dict, Optional, Union
import sys
from pathlib import Path
from planner.filtering import get_available_categories, filter_sights_by_category
from planner.map_utils import generate_map
from planner.osm import fetch_osm_sights
from planner.sights import Sight # Need Sight to convert from API dicts back to objects

import osmnx as ox
from shapely.geometry import Point
import math
import pandas as pd # <-- Import pandas for the comparison table

# Use environment variable for FastAPI URL for flexibility
FASTAPI_URL = os.environ.get("API_URL", "http://localhost:8000")

# Add the project root to sys.path (WalkingVacation folder)
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


CITY_COORDS = {
    "Berlin": (52.5200, 13.4050),
    "Paris": (48.8566, 2.3522),
}

TAGS = {
    "tourism": ["museum", "gallery", "attraction", "viewpoint"],
    "leisure": ["park", "garden"],
}
#TAGS = {
#    "amenity": True, # Matches any amenity
#    "tourism": True, # Matches any tourism feature
#    "leisure": True, # Matches any leisure feature
#    "shop": True # Matches any shop
#}

postcard_messages = {
    "morning": "The city wakes up — golden light and fresh vibes!",
    "afternoon": "Sun high, perfect for outdoor strolls and museums alike.",
    "evening": "As lights flicker on, the city turns magical.",
}

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Tourist Planner", page_icon="🌍")
st.title("🌍 Tourist Planner")

# Initialize session state variables if they don't exist
if "randomize_weather" not in st.session_state:
    st.session_state.randomize_weather = False
if "trigger_plan" not in st.session_state:
    st.session_state.trigger_plan = False
if "generate_forecast" not in st.session_state:
    st.session_state.generate_forecast = False
if "llm_narrate" not in st.session_state:
    st.session_state.llm_narrate = False
if "last_selected_sights" not in st.session_state:
    st.session_state["last_selected_sights"] = []
if "demo_mode_active" not in st.session_state:
    st.session_state.demo_mode_active = False # Initial state is OFF
if "plan_auto_triggered" not in st.session_state:
    st.session_state.plan_auto_triggered = False
if "api_plan_results" not in st.session_state:
    st.session_state.api_plan_results = None
if "display_plan_type" not in st.session_state:
    st.session_state.display_plan_type = "aware"

@st.cache_data(show_spinner=False)
def get_sights_for_city(_location_input: Union[str, Point], tags: Dict[str, Union[List[str], bool]], refresh_data: bool, radius_meters: Optional[int] = None) -> List[Sight]:
    """
    Wrapper around fetch_osm_sights to handle caching.
    It intelligently passes location as str or Point based on type,
    and includes radius_meters when location is a Point.
    """
    # The underscore in _location_input is only for Streamlit's caching.
    # Inside the function, you still refer to it as location_input (without the underscore).
    # So, we'll assign it to a local variable without the underscore for clarity and consistency.
    location_arg = _location_input

    if isinstance(location_arg, Point):
        if radius_meters is None:
            st.error("Internal Error: radius_meters must be provided when location_input is a Point.")
            return []
        return fetch_osm_sights(location=location_arg, tags=tags, refresh=refresh_data, radius_meters=radius_meters)
    else:
        return fetch_osm_sights(location=location_arg, tags=tags, refresh=refresh_data)

@st.cache_data(show_spinner=False)
def get_city_center(city_name: str) -> Point:
    city_name_stripped = city_name.strip()
    if city_name_stripped in CITY_COORDS:
        lat, lon = CITY_COORDS[city_name_stripped]
    else:
        lat, lon = ox.geocode(city_name_stripped)
        CITY_COORDS[city_name_stripped] = (lat, lon) # Update cache
    return Point(lon, lat)


# --- Demo Mode Control ---

# Function to run when demo toggle changes (or when button activates demo)
def handle_demo_toggle_change_old():
    # This function now correctly assumes st.session_state.demo_mode_active
    # has just been set to its desired state (either by toggle or button).
    if st.session_state.demo_mode_active:
        # Demo mode activated, set demo specifics
        st.session_state.user_city = "Paris, France"
        st.session_state.trigger_plan = True # Automatically trigger plan in demo
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False
        st.session_state.plan_auto_triggered = True # Indicate it's auto-triggered by demo
        st.session_state.api_plan_results = None # Clear old results
        st.cache_data.clear() # Clear ALL caches to ensure fresh start for demo
    else:
        # Demo mode deactivated, clear demo specifics
        st.session_state.user_city = "" # Clear user city
        st.session_state.trigger_plan = False
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False
        st.session_state.plan_auto_triggered = False
        st.session_state.api_plan_results = None
        st.cache_data.clear() # Clear ALL caches (important for switching back to manual mode)
def handle_demo_toggle_change():
    # We declare CITY_COORDS as global because we are *assigning a new dictionary* to it.
    # If we were just modifying items *within* the dictionary (e.g., CITY_COORDS['NewCity'] = ...),
    # 'global' wouldn't strictly be necessary in most cases, but for clarity when re-initializing, it's good.
    global CITY_COORDS

    if st.session_state.demo_mode_active:
        # Demo mode activated, set demo specifics
        st.session_state.user_city = "Paris, France" # This will correctly geocode Paris, France
        st.session_state.trigger_plan = True # Automatically trigger plan in demo
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False
        st.session_state.plan_auto_triggered = True # Indicate it's auto-triggered by demo
        st.session_state.api_plan_results = None # Clear old results

        # --- IMPORTANT ADDITION ---
        # Re-initialize CITY_COORDS to its original, correct state.
        # This overwrites any dynamically added or incorrect entries.
        CITY_COORDS = {
            "Berlin": (52.5200, 13.4050),
            "Paris": (48.8566, 2.3522),
        }
        # --- END IMPORTANT ADDITION ---

        st.cache_data.clear() # Clear ALL Streamlit caches (including get_sights_for_city, get_city_center)
    else:
        # Demo mode deactivated, clear demo specifics
        st.session_state.user_city = "Berlin" # <--- Ensure it defaults to Berlin
        st.session_state.trigger_plan = False
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False
        st.session_state.plan_auto_triggered = False
        st.session_state.api_plan_results = None

        # --- IMPORTANT ADDITION ---
        # Re-initialize CITY_COORDS to its original, correct state.
        CITY_COORDS = {
            "Berlin": (52.5200, 13.4050),
            "Paris": (48.8566, 2.3522),
        }
        # --- END IMPORTANT ADDITION ---

        st.cache_data.clear() # Clear ALL Streamlit caches (important for switching back to manual mode)

# Display the main demo toggle - This is now the ONLY control for demo mode.
st.toggle("Activate Demo Mode", key="demo_mode_active", on_change=handle_demo_toggle_change,
          help="Toggle to activate or deactivate the Paris demo mode.")


# --- City Selection ---
city_display_label, potential_city_center = get_user_city_input(CITY_COORDS)

city = None # Tmain city label used downstream
CITY_CENTER = None # actual shapely Point

if potential_city_center is not None:
    # Scenario 1: User selected "Enter coordinates", or a city for which a Point was directly provided
    CITY_CENTER = potential_city_center
    city = city_display_label # Keep the "Coords(...)" label for display purposes
elif city_display_label:
    # Scenario 2: User selected or typed a city name (e.g., "Berlin", "London")
    # For these, we need to geocode if not already in cache.
    try:
        city = city_display_label # Use the human-readable city name for geocoding
        CITY_CENTER = get_city_center(city) # This will call ox.geocode if needed
    except Exception as e:
        st.error(f"Error getting city center for '{city_display_label}': {e}. Please try another city or check its spelling.")
        city = None # Invalidate city if geocoding fails
        CITY_CENTER = None
else:
    # Scenario 3: No valid city input was provided (e.g., empty selection/input)
    city = None
    CITY_CENTER = None
if not city or CITY_CENTER is None:
    st.markdown(
        """
        ### Welcome to the Tourist Planner! 🌍
        Let's start your adventure. Please **select a city** from the dropdown,
        **type a city name**, or **enter coordinates** to begin planning your tour.
        """
    )
    st.stop()

if not city or CITY_CENTER is None:
    st.markdown(
        """
        ### Welcome to the Tourist Planner! 🌍✨
        Let's start your adventure. Please **select a city** from the dropdown,
        **type a city name**, or **enter coordinates** to begin planning your tour.
        """
    )
    st.stop()

# --- Fetch & Filter Sights ---
if st.session_state.demo_mode_active and city == "Paris, France":
    st.info("Loading pre-selected sights from `data/sights.csv` for Paris demo...")
    from planner.data_loader import load_sights_from_csv # Ensure this import is here
    try:
        all_sights = load_sights_from_csv("data/paris_sights_15.csv")
        st.write("Successfully loaded demo sights!")
    except FileNotFoundError:
        st.error("Demo sights file 'data/sights.csv' not found! Please ensure it exists.")
        st.stop()
    refresh_osm_data = False
    st.checkbox("Refresh data from OSM (disabled in demo mode)", value=False, disabled=True)
else:
    if st.session_state.demo_mode_active and city != "Paris, France":
        st.session_state.demo_mode_active = False
        st.session_state.plan_auto_triggered = False
        st.session_state.api_plan_results = None # Clear results if demo mode exited
        st.warning("Demo mode deactivated: city changed.")
        st.rerun()

    # This should be a button, not a checkbox
    if st.button("🔄 Refresh Data from OSM"):
        get_sights_for_city.clear()  # Clears the specific cache for this function
        st.rerun()  # Forces a rerun to re-execute the function
    with st.spinner(f"Fetching points of interest for {city}..."):
        if isinstance(city, str) and not city.startswith("Coords("):  # It's a proper city name string
            all_sights = get_sights_for_city(_location_input=city, tags=TAGS, refresh_data=True)
        elif isinstance(CITY_CENTER, Point):  # It's a Point (from coords input or demo mode's geocoding)
            # Ensure radius is available when using a Point
            if 'radius_for_point_query' not in st.session_state:
                st.session_state.radius_for_point_query = 5000  # Default if somehow unset

            all_sights = get_sights_for_city(_location_input=CITY_CENTER,
                                             tags=TAGS,
                                             refresh_data=True,
                                             radius_meters=st.session_state.radius_for_point_query)
        else:
            st.warning("Could not determine valid location type for fetching sights. Please check city input.")
            st.stop()

if not all_sights:
    st.warning(f"No sights found for {city} using the current tags. Try a larger city or adjust filter tags.")
    # Add a print to the console for more detail
    print(f"DEBUG: No sights found for {city} with TAGS: {TAGS}")
    print(f"DEBUG: all_sights is empty after fetch_osm_sights for {city}")
    st.stop()
else:
    print(f"DEBUG: Successfully fetched {len(all_sights)} sights for {city} with TAGS: {TAGS}")
    # Print the first few sights to inspect their names and categories
    for i, sight in enumerate(all_sights[:5]):
        print(f"DEBUG: Sight {i+1}: Name={sight.name}, Category={sight.category}, Loc=({sight.location.y:.2f}, {sight.location.x:.2f})")

def is_valid_sight(sight):
    return bool(sight.name and str(sight.name).strip().lower() != 'nan' and sight.location is not None and sight.category and str(sight.category).strip() != '')

valid_sights = [s for s in all_sights if is_valid_sight(s)]

if not valid_sights:
    st.warning("No valid sights available after initial filtering. Try adjusting your city or tags, or refresh the data.")
    st.stop()

categories = get_available_categories(valid_sights)
if st.session_state.demo_mode_active:
    st.markdown("### Filter by category (all selected for demo)")
    selected_categories = st.multiselect("Filter by category", categories, default=categories, disabled=True)
else:
    selected_categories = st.multiselect("Filter by category", categories, default=categories)
filtered_sights = filter_sights_by_category(valid_sights, selected_categories)

# --- Sight Selection with Limit ---
sight_names = [s.name for s in filtered_sights]
MAX_SIGHTS_FOR_PLAN = 15 #10

if len(sight_names) > MAX_SIGHTS_FOR_PLAN:
    st.info(f"For optimal planning performance, please select up to {MAX_SIGHTS_FOR_PLAN} sights for your tour. The algorithm will automatically use the first {MAX_SIGHTS_FOR_PLAN} if more are chosen.")
    default_selected = sight_names[:MAX_SIGHTS_FOR_PLAN]
else:
    default_selected = sight_names

if st.session_state.demo_mode_active:
    st.markdown(f"### Select sights to include in your plan (auto-selected for demo)")
    selected_sight_names = st.multiselect(
        f"Select sights to include in your plan (max {MAX_SIGHTS_FOR_PLAN})",
        sight_names,
        default=default_selected,
        disabled=False
    )
else:
    selected_sight_names = st.multiselect(
        f"Select sights to include in your plan (max {MAX_SIGHTS_FOR_PLAN})",
        sight_names,
        default=default_selected
    )

if len(selected_sight_names) > MAX_SIGHTS_FOR_PLAN:
    st.warning(f"You've selected {len(selected_sight_names)} sights. Only the first {MAX_SIGHTS_FOR_PLAN} will be used for planning.")
    selected_sight_names = selected_sight_names[:MAX_SIGHTS_FOR_PLAN]

final_sights = [s for s in filtered_sights if s.name in selected_sight_names]

if not final_sights:
    st.info("No sights selected for your tour plan. Please adjust your filters or make sure you've selected sights from the list above.")
    st.stop()

# --- Map Display ---
center_map_on = final_sights[0].location if final_sights else CITY_CENTER
map_obj = generate_map(final_sights, center_map_on)
st.subheader("Map of Selected Sights")
st_folium(map_obj, width=700, height=500)

st.write(f"Found {len(filtered_sights)} filtered sights.")
st.write(f"**{len(final_sights)} sights selected for your plan (max {MAX_SIGHTS_FOR_PLAN}).**")

# --- Re-plan Trigger Logic ---
def clean_sight_list_names(sight_list_names):
    return [s for s in sight_list_names if isinstance(s, str) and not (isinstance(s, float) and math.isnan(s))]

safe_selected_names_current = clean_sight_list_names(selected_sight_names)
safe_selected_names_last = clean_sight_list_names(st.session_state.get("last_selected_sights", []))

if set(safe_selected_names_current) != set(safe_selected_names_last):
    st.session_state["trigger_plan"] = False
    st.session_state["last_selected_sights"] = safe_selected_names_current
    st.session_state.plan_auto_triggered = False
    st.session_state.api_plan_results = None # Clear old plan results

# --- Plan Tour Section ---
st.subheader("Plan Your Tour")

if len(final_sights) < 2:
    st.warning("Please select at least two sights to plan a tour.")
    st.stop()

if st.session_state.demo_mode_active and not st.session_state.get("plan_auto_triggered", False):
    st.session_state.trigger_plan = True
    st.session_state.plan_auto_triggered = True
    st.rerun()
else:
    if st.button("🔄 Replan Tour"):
        st.session_state.trigger_plan = True
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False
        st.session_state.plan_auto_triggered = False
        st.session_state.api_plan_results = None # Clear old plan results

if st.session_state.trigger_plan:
    from planner.weather_utils import fetch_or_generate_forecast, get_test_date
    test_date = get_test_date(days_ahead=0)

    if st.session_state.demo_mode_active and not st.session_state.generate_forecast:
        st.session_state.forecast = fetch_or_generate_forecast(
            CITY_CENTER,
            randomize=False,
            target_date=test_date
        )
        st.session_state.generate_forecast = True
        st.rerun()
    else:
        randomize_weather_toggle = st.checkbox("🎲 Randomize weather forecast (for testing)", key="randomize_weather_toggle")
        if st.button("☁️ Generate Forecast") or not st.session_state.generate_forecast:
            st.session_state.forecast = fetch_or_generate_forecast(
                CITY_CENTER,
                randomize=randomize_weather_toggle,
                target_date=test_date
            )
            st.session_state.generate_forecast = True

    forecast = st.session_state.get("forecast", None)
    if forecast:
        st.info(f"Weather forecast: **{forecast}**")
    else:
        st.info("Press 'Generate Forecast' to get the weather forecast.")
        st.stop()

    # --- API Call to get BOTH plans and metrics ---
    sight_data_for_api = [
        {"name": s.name, "lat": s.location.y, "lon": s.location.x, "category": s.category,
         "weather_suitability": s.weather_suitability}
        for s in final_sights
    ]

    plan_request_body = {
        "city": city,
        "mode": "walking",
        "sights": sight_data_for_api,
        "forecast_data": forecast
    }

    if st.session_state.api_plan_results is None: # Only call API if results not already in session state
        with st.spinner("Planning your tour via API (comparing algorithms)..."):
            try:
                response = requests.post(f"{FASTAPI_URL}/plan", json=plan_request_body)
                response.raise_for_status()
                st.session_state.api_plan_results = response.json() # Store the full response
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to FastAPI at {FASTAPI_URL}. Is the API running and accessible?")
                st.stop()
            except requests.exceptions.RequestException as e:
                st.error(f"Error from API during tour planning: {e}. Please check API logs for details.")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred during API communication: {e}")
                st.stop()

    # --- Display Plan Comparison Table ---
    if st.session_state.api_plan_results:
        results = st.session_state.api_plan_results

        comparison_data = {
            "Metric": ["Calculation Time (s)", "Total Length (m)"],
            "Weather-Aware Plan": [
                f"{results['aware_time_seconds']:.2f}",
                f"{results['aware_length_meters']:.2f}"
            ],
            "Iterative Plan": [
                f"{results['iterative_time_seconds']:.2f}",
                f"{results['iterative_length_meters']:.2f}"
            ]
        }
        comparison_df = pd.DataFrame(comparison_data)
        st.subheader("Algorithm Comparison")
        st.dataframe(comparison_df, hide_index=True)

        # --- Plan Selection ---
        st.session_state.display_plan_type = st.radio(
            "Select which plan to display:",
            options=["Weather-Aware Plan", "Iterative Plan"],
            index=0 if results['selected_plan_type'] == 'aware' else 1, # Default to aware or iterative
            key="plan_selector"
        )

        # Convert selected plan's sights from dicts back to Sight objects
        if st.session_state.display_plan_type == "Weather-Aware Plan":
            current_tour_plan_data = results['aware_plan']
        else:
            current_tour_plan_data = results['iterative_plan']

        tour_plan_to_display = {}
        for slot, sights_out_list in current_tour_plan_data.items():
            tour_plan_to_display[slot] = [
                Sight(name=s_out['name'], location=Point(s_out['lon'], s_out['lat']),
                      category=s_out.get('category', 'unknown'),
                      weather_suitability=s_out.get('weather_suitability', ['any']))
                for s_out in sights_out_list
            ]

        # --- Display the Selected Plan ---
        from planner.display import st_render_plan
        from planner.get_route import plot_full_day_tour

        fmap = plot_full_day_tour(tour_plan_to_display, CITY_CENTER, mode="walking")

        st_render_plan(
            st,
            tour_plan=tour_plan_to_display,
            forecast=forecast,
            postcards=postcard_messages,
            fmap=fmap
        )

        # --- LLM Narration Section ---
        if st.session_state.demo_mode_active and not st.session_state.llm_narrate:
            st.session_state.llm_narrate = True
            st.rerun()
        else:
            if st.button("💬 LLM Narrate"):
                st.session_state.llm_narrate = True

        if st.session_state.llm_narrate:
            st.subheader("Tour Narrations")
            for slot, sights in tour_plan_to_display.items(): # Use the currently displayed plan for narration
                sight_names_for_narration = [s.name for s in sights]
                if not sight_names_for_narration:
                    st.info(f"No sights for {slot.title()} to narrate.")
                    continue

                narration_request_body = {
                    "slot": slot,
                    "city": city,
                    "sights": sight_names_for_narration
                }
                with st.spinner(f"Generating {slot.title()} narration..."):
                    try:
                        narration_response = requests.post(f"{FASTAPI_URL}/narrate", json=narration_request_body)
                        narration_response.raise_for_status()
                        narration = narration_response.json()["text"]
                        st.success(f"**{slot.title()} Narration:**")
                        st.markdown(f"> *{narration}*")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching narration for {slot} via API: {e}. Falling back to template.")
                        st.markdown(f"**{slot.title()} Narration (Template Fallback):**")
                        st.markdown(f"> *{postcard_messages.get(slot, 'No template narration available.')}*")
                    except KeyError:
                        st.error(f"API response for narration missing 'text' key for {slot}. Falling back to template.")
                        st.markdown(f"**{slot.title()} Narration (Template Fallback):**")
                        st.markdown(f"> *{postcard_messages.get(slot, 'No template narration available.')}*")
    else:
        st.info("No plan generated yet. Select sights and click 'Replan Tour'.")
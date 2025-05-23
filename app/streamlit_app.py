import os
import streamlit as st
from streamlit_folium import st_folium
from app.ui import get_user_city_input #a
import sys
from pathlib import Path
from planner.filtering import get_available_categories, filter_sights_by_category
from planner.map_utils import generate_map
from planner.base_planner import DayPlanner
from planner.osm import fetch_osm_sights
from planner.sights import Sight

########################
# For batch jobs and testing use tourist_planner!
# Execute the app in the browser with:
# python -m streamlit run app/streamlit_app.py

# Add the project root to sys.path (WalkingVacation folder)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("Updated sys.path:", sys.path)
print("Current working directory:", os.getcwd())
print("sys.path:", sys.path)

print("Checking project structure:")
print(Path(__file__).resolve().parent)
print(list(Path(__file__).resolve().parents[1].glob('planner')))

import osmnx as ox
from shapely.geometry import Point

CITY_COORDS = {
    "Berlin": (52.5200, 13.4050),
    "Paris": (48.8566, 2.3522),
}

TAGS = {
    "tourism": ["museum", "gallery", "attraction", "viewpoint"],
    "leisure": ["park", "garden"],
}

# Dummy postcard messages
postcard_messages = {
    "morning": "The city wakes up — golden light and fresh vibes!",
    "afternoon": "Sun high, perfect for outdoor strolls and museums alike.",
    "evening": "As lights flicker on, the city turns magical.",
}

# Sample sights (replace with real data or load from file)
all_sights = [
    Sight(name="Museum A", location=Point(13.4, 52.52), category="museum", weather_suitability=["rainy", "any"]),
    Sight(name="Park B", location=Point(13.41, 52.515), category="park", weather_suitability=["sunny"]),
    Sight(name="Gallery C", location=Point(13.39, 52.518), category="gallery", weather_suitability=["cloudy", "any"]),
]
if "randomize_weather" not in st.session_state:
    st.session_state.randomize_weather = False

@st.cache_data(show_spinner=False)
def get_sights_for_city(city, tags, refresh):
    return fetch_osm_sights(city, tags, refresh)

def get_city_center(city_name: str) -> Point:
    city_name = city_name.strip()
    if city_name in CITY_COORDS:
        lat, lon = CITY_COORDS[city_name]
    else:
        lat, lon = ox.geocode(city_name)
        CITY_COORDS[city_name] = (lat, lon)  # cache for later
    return Point(lon, lat)

refresh = st.checkbox("Refresh data from OSM", value=False)

st.title("🌍 Tourist Planner")

city, CITY_CENTER = get_user_city_input(CITY_COORDS)

if not city or CITY_CENTER is None:
    st.info("Please select or enter a valid city or coordinates to continue.")
    st.stop()

# Fetch sights once city is set
with st.spinner(f"Fetching points of interest for {city}..."):
    all_sights = get_sights_for_city(city, TAGS, refresh)

if not all_sights:
    st.warning("No sights found. Try a larger city or change tags.")
    st.stop()

def is_valid_sight(sight):
    # Check name: must be string, non-empty, not 'nan' string
    if not sight.name or str(sight.name).strip().lower() == 'nan':
        return False

    # Check location: should not be None (you can extend to verify Point validity if needed)
    if sight.location is None:
        return False

    # Check category: must be non-empty string
    if not sight.category or str(sight.category).strip() == '':
        return False

    return True


valid_sights = [s for s in all_sights if is_valid_sight(s)]

if valid_sights:
    categories = get_available_categories(valid_sights)
    selected_categories = st.multiselect("Filter by category", categories, default=categories)
    st.markdown("### Filter sights by selected categories")
    filtered_sights = filter_sights_by_category(valid_sights, selected_categories)
else:
    st.warning("No valid sights available.")

# Select which sights to include
sight_names = [s.name for s in filtered_sights]
selected_sight_names = st.multiselect("Select sights to include in your plan", sight_names, default=sight_names)
final_sights = [s for s in filtered_sights if s.name in selected_sight_names]


if final_sights:
    center = final_sights[0].location
else:
    center = CITY_CENTER

map_obj = generate_map(final_sights, center)
st.subheader("Map of Sights")
st_folium(map_obj, width=700, height=500)

st.write(f"Found {len(filtered_sights)} filtered sights.")
st.write(f"Found {len(final_sights)} sights selected for your plan.")

# Track if selected sights changed → trigger re-plan
if "last_selected_sights" not in st.session_state:
    st.session_state["last_selected_sights"] = []
    
import math

def clean_sight_list(sight_list):
    return [s for s in sight_list if isinstance(s, str) and not (isinstance(s, float) and math.isnan(s))]

# Safely update session state
safe_selected_names = clean_sight_list(selected_sight_names)
last_selected = clean_sight_list(st.session_state.get("last_selected_sights", []))

if set(safe_selected_names) != set(last_selected):
    st.session_state["trigger_plan"] = False
    st.session_state["last_selected_sights"] = safe_selected_names


if final_sights:
    st.subheader("Plan Your Tour")

    # Step 1: Create persistent trigger flags in session_state
    if "trigger_plan" not in st.session_state:
        st.session_state.trigger_plan = False

    if "generate_forecast" not in st.session_state:
        st.session_state.generate_forecast = False

    if "llm_narrate" not in st.session_state:
        st.session_state.llm_narrate = False

    # Step 2: Buttons with callbacks to set session_state flags
    if st.button("🔄 Replan Tour"):
        st.session_state.trigger_plan = True
        # Reset dependent flags
        st.session_state.generate_forecast = False
        st.session_state.llm_narrate = False

    if st.session_state.trigger_plan:
        planner = DayPlanner()
        from planner.weather_utils import fetch_or_generate_forecast, get_test_date
        test_date = get_test_date(days_ahead=2)

        randomize_weather = st.checkbox("🎲 Randomize weather forecast (for testing)", key="randomize_weather")

        if st.button("☁️ Generate Forecast") or not st.session_state.generate_forecast:
            st.session_state.forecast = fetch_or_generate_forecast(
                CITY_CENTER,
                randomize=randomize_weather,
                date=test_date
            )
            st.session_state.generate_forecast = True

        forecast = st.session_state.get("forecast", None)
        if forecast:
            st.write(f"Weather forecast: {forecast}")
        else:
            st.info("Press 'Generate Forecast' to get the weather forecast.")

        if len(final_sights) < 2:
            st.warning("Please select at least two sights to plan a route.")
            st.stop()

        plan, weather, cards, tour_plan = planner.plan(
            final_sights,
            CITY_CENTER,
            mode="walking",
            weather_forecast=forecast
        )

        from planner.display import st_render_plan
        from planner.get_route import plot_full_day_tour

        fmap = plot_full_day_tour(tour_plan, CITY_CENTER)

        st_render_plan(
            st,
            tour_plan=tour_plan,
            forecast=forecast,
            postcards=postcard_messages,
            fmap=fmap
        )

        # Step 3: LLM Narrate button with session_state tracking
        if st.button("💬 LLM Narrate") or st.session_state.llm_narrate:
            st.session_state.llm_narrate = True
            st.write("Narration triggered!")  # Debug line
            try:
                from planner.genai import narrate
            except ImportError as e:
                st.error(f"Failed to import LLM narration: {e}")
            else:
                for slot, sights in tour_plan.items():
                    narration = narrate(slot, city, [s.name for s in sights], use_template=True)
                    st.success(f"**{slot.title()} narration:** {narration}")
else:
    st.info("Adjust filters or refresh to see available sights.")


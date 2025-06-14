# main.py
import re

from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any # Import Dict, Any for forecast_data

from meteostat import Point
from pydantic import BaseModel, Field
import osmnx as ox
from planner.base_planner import DayPlanner
from planner.genai import narrate
from planner.data_loader import load_sights_from_csv
from planner.sights import Sight
from planner.weather import get_weather_forecast
from shapely.geometry import Point

app = FastAPI(title="CityTour-Planning API")

class NarrateRequest(BaseModel):
    slot: str
    city: str
    sights: List[str]

# api/main.py
class SightOut(BaseModel):
    name: str
    lat: float
    lon: float
    category: Optional[str] = None # <-- Add this line
    weather_suitability: Optional[List[str]] = Field(default_factory=list) # <-- Add this line

# === Request Models ===
# For deserializing sights from the request
class SightIn(BaseModel):
    name: str
    lat: float
    lon: float
    category: Optional[str] = None # Make it optional if not always provided
    weather_suitability: Optional[List[str]] = Field(default_factory=list) # List of strings

class PlanRequest(BaseModel):
    city: str
    # We will now rely on the 'sights' list provided by the UI, not categories for filtering
    # categories: Optional[List[str]] = None # Can remove this if you pass specific sights
    mode: str = "walking"
    sights: List[SightIn] # New: list of sights chosen by the UI
    forecast_data: Optional[Dict[str, Any]] = None # New: to pass forecast data if already generated

# New Pydantic Model for the comprehensive plan response
class PlanComparisonResponse(BaseModel):
    aware_plan: Dict[str, List[SightOut]] # Dictionary of slot -> list of SightOut
    aware_time_seconds: float
    aware_length_meters: float
    iterative_plan: Dict[str, List[SightOut]]
    iterative_time_seconds: float
    iterative_length_meters: float
    selected_plan_type: str # 'aware' or 'iterative'

# Helper function to convert SightIn to Sight object
def convert_sight_in_to_sight(sight_in: SightIn) -> Sight:
    return Sight(
        name=sight_in.name,
        location=Point(sight_in.lon, sight_in.lat),
        category=sight_in.category,
        weather_suitability=sight_in.weather_suitability
    )

# Helper function to convert Sight object to SightOut (for response)
def convert_sight_to_sight_out(sight: Sight) -> SightOut:
    return SightOut(
        name=sight.name,
        lat=sight.location.y,
        lon=sight.location.x,
        category=sight.category,
        weather_suitability=sight.weather_suitability
    )




# === Helper Functions ===

CITY_CENTER_LOOKUP = {
    "paris": (48.8566, 2.3522),
    "berlin": (52.52, 13.405),
    "rome": (41.9028, 12.4964),
    # Add more cities if needed
}

def get_city_center(city: str) -> Point:
    slug = city.split(",")[0].strip().lower()
    lat, lon = CITY_CENTER_LOOKUP.get(slug, (48.8566, 2.3522)) # Default: Paris
    return Point(lon, lat)# Default: Paris

def point_to_dict(point):
    return {"lat": point.y, "lon": point.x}

def convert_sight(sight) -> SightOut:
    return SightOut(
        name=sight.name,
        lat=sight.location.y,
        lon=sight.location.x
    )

# === API Routes ===

@app.post("/plan_old")
def plan(req: PlanRequest):
    print("\n--- Received Plan Request ---")
    print(f"City: {req.city}")
    print(f"Mode: {req.mode}")
    print(f"Forecast Data: {req.forecast_data is not None}")
    print(f"Sights Type: {type(req.sights)}")
    print(f"Number of Sights: {len(req.sights) if isinstance(req.sights, list) else 'Not a list'}")
    # This will print the raw JSON representation of the request body
    print("Sights data (raw JSON):")
    for s_item in req.sights: # Safely iterate to print each SightIn
        print(s_item.model_dump_json(indent=2)) # Use model_dump_json for Pydantic v2+
    print("-----------------------------\n")


    planner = DayPlanner()

    # Convert incoming SightIn objects to your internal Sight objects
    # You'll need to define your Sight class to accept category and weather_suitability in its constructor
    # If your Sight class is in planner/sights.py, ensure it handles these.
    internal_sights = [
        Sight(
            name=s.name,
            location=Point(s.lon, s.lat),
            category=s.category, # Now available from request
            weather_suitability=s.weather_suitability # Now available from request
        ) for s in req.sights
    ]

    # Get city center (still needed for context, but not for fetching sights from CSV)
    city_center = get_city_center(req.city)

    # Use the forecast from the request, or generate if not provided
    if req.forecast_data:
        forecast = req.forecast_data
    else:
        # Fallback: if Streamlit didn't send it (e.g., older version or initial load)
        # This will fetch again based on current time and location
        city_center_for_forecast = get_city_center(req.city)
        # Need to import fetch_or_generate_forecast and get_test_date from planner.weather_utils
        from planner.weather_utils import fetch_or_generate_forecast, get_test_date
        test_date = get_test_date(days_ahead=2)
        # --- CHANGE THIS LINE ---
        forecast = fetch_or_generate_forecast(city_center_for_forecast, date=test_date)  # Pass the Point object
    # Now call the planner with the received sights and forecast
    plan_result, weather, postcards, tour_plan = planner.plan(
        internal_sights, # Use the sights from the request
        city_center,
        req.mode,
        forecast
    )

    # Convert back to SightOut for response (your existing convert_sight function is fine)
    result_out = {slot: [convert_sight(s) for s in sights] for slot, sights in tour_plan.items()}
    return result_out

@app.post("/plan", response_model=PlanComparisonResponse)
async def plan(req: PlanRequest):

    # Determine city_center_point
    city_center_point = None

    # Check if the city field is a coordinate string
    if req.city.startswith("Coords("):
        # Option 1: Extract coordinates directly from the "Coords(...)" string
        # This is good if the 'city' field is *always* exact
        match = re.match(r"Coords\(([^,]+),\s*([^)]+)\)", req.city)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            city_center_point = Point(lon, lat)  # Shapely Point expects (longitude, latitude)
        else:
            # Fallback if the regex doesn't match, though it should if frontend sends it correctly
            # Or raise an error if the format is strictly expected
            raise HTTPException(status_code=400, detail=f"Invalid 'Coords(...)' format in city field: {req.city}")

        # Option 2 (Alternative/Fallback): Calculate centroid from provided sights
        # This is more robust if you might have many sights or want a true center of the selected area
        # if req.sights:
        #     avg_lat = sum(s.lat for s in req.sights) / len(req.sights)
        #     avg_lon = sum(s.lon for s in req.sights) / len(req.sights)
        #     city_center_point = Point(avg_lon, avg_lat)
        # else:
        #     raise HTTPException(status_code=400, detail="Cannot plan for coordinates without sights data.")

    else:
        # It's a city name, so geocode it using OSMnx
        try:
            # osmnx.geocode returns (latitude, longitude)
            # Point expects (longitude, latitude)
            lat, lon = ox.geocode(req.city)
            city_center_point = Point(lon, lat)
        except ox._errors.InsufficientResponseError:
            raise HTTPException(status_code=404,
                                detail=f"Could not geocode city '{req.city}'. Please check spelling or try another city.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error geocoding city '{req.city}': {e}")

    # --- Ensure city_center_point was successfully determined ---
    if city_center_point is None:
        raise HTTPException(status_code=500, detail="Failed to determine a valid city center point for planning.")

    sights_for_planner = [convert_sight_in_to_sight(s_in) for s_in in req.sights]

    forecast = req.forecast_data
    if forecast is None:
        try:
            from planner.weather_utils import get_weather_forecast # Ensure this import is here
            forecast = get_weather_forecast(city_center_point)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not fetch weather forecast: {e}")

    planner = DayPlanner()

    plan_results = await planner.plan(sights_for_planner, city_center_point, req.mode, forecast)

    # --- CRITICAL CHANGES HERE ---
    # Access the "tour_plan" key within "aware_plan" and "iterative_plan"
    aware_tour_plan_data = plan_results["aware_plan"]["tour_plan"]
    iterative_tour_plan_data = plan_results["iterative_plan"]["tour_plan"]

    aware_plan_out = {
        slot: [convert_sight_to_sight_out(s) for s in sights_list]
        for slot, sights_list in aware_tour_plan_data.items() # Use the specific tour_plan data
    }
    iterative_plan_out = {
        slot: [convert_sight_to_sight_out(s) for s in sights_list]
        for slot, sights_list in iterative_tour_plan_data.items() # Use the specific tour_plan data
    }

    return PlanComparisonResponse(
        aware_plan=aware_plan_out,
        # Access times/lengths directly from the 'aware_plan' dictionary
        aware_time_seconds=plan_results["aware_plan"]["planning_time_seconds"],
        aware_length_meters=plan_results["aware_plan"]["haversine_total_subtour_length_meters"],#["total_length_meters"],
        iterative_plan=iterative_plan_out,
        iterative_time_seconds=plan_results["iterative_plan"]["planning_time_seconds"], # Note: using planning_time_seconds for iterative as well based on your structure
        iterative_length_meters=plan_results["iterative_plan"]["haversine_total_subtour_length_meters"],#["total_length_meters"],
        selected_plan_type=plan_results["selected_plan_type"]
    )

@app.post("/narrate")
def narrate_endpoint(req: NarrateRequest):
    narration = narrate(req.slot, req.city, req.sights, use_template=True)
    return {"text": narration}

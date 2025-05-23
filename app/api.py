# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from planner.base_planner import DayPlanner
from planner.genai import narrate
from planner.data_loader import load_sights_from_csv
from planner.weather import get_weather_forecast

app = FastAPI(title="CityTour-Planning API")

# === Request Models ===

class PlanRequest(BaseModel):
    city: str
    categories: Optional[List[str]] = None
    mode: str = "walking"  # walking, cycling, driving


class NarrateRequest(BaseModel):
    slot: str
    city: str
    sights: List[str]

class SightOut(BaseModel):
    name: str
    lat: float
    lon: float

# === Helper Functions ===

CITY_CENTER_LOOKUP = {
    "paris": (48.8566, 2.3522),
    "berlin": (52.52, 13.405),
    "rome": (41.9028, 12.4964),
    # Add more cities if needed
}

def get_city_center(city: str) -> tuple:
    slug = city.split(",")[0].strip().lower()
    return CITY_CENTER_LOOKUP.get(slug, (48.8566, 2.3522))  # Default: Paris

def point_to_dict(point):
    return {"lat": point.y, "lon": point.x}

def convert_sight(sight) -> SightOut:
    return SightOut(
        name=sight.name,
        lat=sight.location.y,
        lon=sight.location.x
    )

# === API Routes ===

@app.post("/plan")
def plan(req: PlanRequest):
    planner = DayPlanner()

    city_center = get_city_center(req.city)
    sights = load_sights_from_csv("data/sights.csv")  # Or resolve CSV based on city

    forecast = get_weather_forecast(city_center[0], city_center[1])

    plan, weather, postcards, tour_plan = planner.plan(sights, city_center, req.mode, forecast)
    # Convert plan_result (assume it's a dict of slots -> list of sights)
    '''serializable_plan = {}
    for slot, sights in plan_result.items():
        serializable_plan[slot] = [s.to_dict() for s in sights]  # convert each sight

    return serializable_plan'''

    # Convert to dict[str, list[SightOut]] so FastAPI can encode it
    result_out = {slot: [convert_sight(s) for s in sights] for slot, sights in tour_plan.items()}

    return result_out


@app.post("/narrate")
def narrate_endpoint(req: NarrateRequest):
    narration = narrate(req.slot, req.city, req.sights, use_template=True)
    return {"text": narration}

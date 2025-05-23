#Weather.py
# planner/weather.py
from datetime import datetime

# Example weather conditions for each time slot
MOCK_WEATHER_FORECAST = {
    "morning": "sunny",
    "afternoon": "rainy",
    "evening": "cloudy",
}

def get_weather_forecast(city_center, date):
    """
    Return a dict of weather condition by time slot for the given date.
    Replace this with real API call if desired.
    """
    # For now, return the mock data regardless of input
    return MOCK_WEATHER_FORECAST

def is_weather_suitable(sight, weather_condition):
    """
    Check if a sight's weather_suitability includes the current weather condition.
    sight.weather_suitability is a list like ['sunny', 'any']
    """
    # 'any' means always suitable
    if 'any' in sight.weather_suitability:
        return True
    return weather_condition in sight.weather_suitability


#Tour.py
# planner/tour.py
#from planner.weather import is_weather_suitable
#from planner.utils import distance

def split_day_into_slots():
    """Define time slots, can be extended as needed."""
    return {
        "morning": ("08:00", "12:00"),
        "afternoon": ("12:00", "17:00"),
        "evening": ("17:00", "21:00"),
    }

def optimize_route(start_point, sights, mode="walking"):
    """
    Simple nearest neighbor route optimization.
    start_point: (lat, lon)
    sights: list of sight objects with .location attribute (shapely Point or tuple)
    Returns sights ordered by optimized visiting sequence.
    """
    if not sights:
        return []

    unvisited = sights[:]
    route = []
    current = start_point

    while unvisited:
        # Find nearest sight to current location
        nearest = min(unvisited, key=lambda s: distance(current, s.location))
        route.append(nearest)
        current = (nearest.location.y, nearest.location.x)  # Assuming shapely Point(x=lon, y=lat)
        unvisited.remove(nearest)

    return route

def create_weather_aware_tour(sights, weather_forecast, city_center):
    """
    Create a tour divided by time slots, only including sights suitable for the weather.
    Returns dict: { time_slot: [ordered sights] }
    """
    time_slots = split_day_into_slots()
    tour_plan = {}

    for slot in time_slots.keys():
        weather = weather_forecast.get(slot, "unknown")
        suitable_sights = [s for s in sights if is_weather_suitable(s, weather)]
        ordered_sights = optimize_route(city_center, suitable_sights)
        tour_plan[slot] = ordered_sights

    return tour_plan


#planner.py

# planner/utils.py
from math import sqrt

def distance(p1, p2):
    """
    p1, p2: tuples (lat, lon) or shapely Points.
    Returns Euclidean distance (approximate).
    """
    # If input is shapely Point, convert to (lat, lon)
    if hasattr(p1, 'x') and hasattr(p1, 'y'):
        p1 = (p1.y, p1.x)
    if hasattr(p2, 'x') and hasattr(p2, 'y'):
        p2 = (p2.y, p2.x)

    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

#adjustment to tourist_planner

from planner.weather import get_weather_forecast
#from planner.tour import create_weather_aware_tour, split_day_into_slots



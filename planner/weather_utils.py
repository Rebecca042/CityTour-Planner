# planner/weather_utils.py

import random
from datetime import datetime, timedelta
from shapely.geometry import Point
import streamlit as st

from .weather import get_weather_forecast  #p


def get_test_date(days_ahead: int = 2) -> datetime:
    """Return the test date, e.g., 2 days in the future."""
    return datetime.now() + timedelta(days=days_ahead)


def generate_random_forecast() -> dict:
    """Generate a randomized forecast dictionary."""
    return {
        "morning": random.choice(["sunny", "cloudy", "rainy"]),
        "afternoon": random.choice(["sunny", "cloudy", "rainy"]),
        "evening": random.choice(["sunny", "cloudy", "rainy"]),
    }


def fetch_or_generate_forecast(center: Point, randomize: bool = False, date: datetime = None) -> dict:
    """Handles fetching or generating weather forecast based on flags and city center."""
    if date is None:
        date = get_test_date()

    if randomize:
        forecast = generate_random_forecast()
        st.write("🔮 Random forecast generated")
    else:
        forecast = get_weather_forecast(center.y, center.x, date=date)
        st.write("📡 Real forecast retrieved")

    return forecast

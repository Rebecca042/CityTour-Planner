import pandas as pd
from meteostat import Point as MeteostatPoint, Daily, units, Hourly
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional

from shapely.geometry import Point

def get_weather_forecast(location: Point, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Fetches the weather forecast for a given location and date.
    Args:
        location: A shapely.geometry.Point object (lon, lat) for the location.
        target_date: The date for which to get the forecast.
    Returns:
        A dictionary with weather conditions for 'morning', 'afternoon', 'evening'.
    """
    # Convert the Shapely point to a metostat point
    meteostat_location = MeteostatPoint(location.y, location.x) # location.y is latitude, location.x is longitude

    if target_date is None:
        current_date = datetime.now().date()  # Get just the date part for combining
    else:
        current_date = target_date  # Use the provided date

    # Define time slots as datetime ranges
    morning_start = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=8)
    morning_end = morning_start + timedelta(hours=4)  # 08:00-12:00
    afternoon_start = morning_end  # 12:00
    afternoon_end = afternoon_start + timedelta(hours=5)  # 12:00-17:00
    evening_start = afternoon_end  # 17:00
    evening_end = evening_start + timedelta(hours=4)  # 17:00-21:00

    # Fetch hourly data for the full day (say 8:00 - 21:00)
    start_time = morning_start
    end_time = evening_end
    data = Hourly(meteostat_location, start_time, end_time)
    df = data.fetch()

    if df.empty:
        return {"morning": "unknown", "afternoon": "unknown", "evening": "unknown"}


    def summarize_slot(slot_start, slot_end):
        # Ensure comparison with timezone-naive datetimes if df.index is naive, or convert if needed
        slot_data = df[(df.index >= slot_start) & (df.index < slot_end)]
        if slot_data.empty:
            return "unknown"

        # Simple rule: if total precipitation > threshold -> rainy
        # Use .get() and an empty Series as fallback for safe sum on potentially missing columns
        if slot_data.get('prcp', pd.Series(dtype='float64')).sum() > 1.0:
            return "rainy"

        # Average temperature
        # Use .get() and an empty Series as fallback for safe mean on potentially missing columns
        avg_temp = slot_data.get('temp', pd.Series(dtype='float64')).mean()
        if pd.notna(avg_temp): # Check if mean is not NaN
            if avg_temp > 20:
                return "sunny"
            else:
                return "cloudy"
        else:
            return "unknown" # If no temp data

    forecast = {
        "morning": summarize_slot(morning_start, morning_end),
        "afternoon": summarize_slot(afternoon_start, afternoon_end),
        "evening": summarize_slot(evening_start, evening_end),
    }

    return forecast

def get_weather_condition(lat, lon, date):
    location = Point(lat, lon)
    data = Daily(location, date, date)
    df = data.fetch()
    if df.empty:
        return "unknown"
    weather = df.iloc[0]
    if weather['prcp'] > 1.0:
        return "rainy"
    elif weather['tavg'] > 20:
        return "sunny"
    else:
        return "cloudy"
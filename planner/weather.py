from meteostat import Point, Daily, Hourly
from datetime import datetime, timedelta

def get_weather_forecast(lat, lon, date=None):
    """
    Fetch hourly weather data from Meteostat for the date and location,
    then summarize into time slots: morning, afternoon, evening.
    Returns dict like {"morning": "sunny", "afternoon": "rainy", "evening": "cloudy"}
    """
    if date is None:
        date = datetime.now()

    location = Point(lat, lon)

    # Define time slots as datetime ranges
    morning_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=8)
    morning_end = morning_start + timedelta(hours=4)  # 08:00-12:00
    afternoon_start = morning_end  # 12:00
    afternoon_end = afternoon_start + timedelta(hours=5)  # 12:00-17:00
    evening_start = afternoon_end  # 17:00
    evening_end = evening_start + timedelta(hours=4)  # 17:00-21:00

    # Fetch hourly data for the full day (say 8:00 - 21:00)
    start_time = morning_start
    end_time = evening_end
    data = Hourly(location, start_time, end_time)
    df = data.fetch()

    if df.empty:
        return {"morning": "unknown", "afternoon": "unknown", "evening": "unknown"}

    def summarize_slot(slot_start, slot_end):
        slot_data = df[(df.index >= slot_start) & (df.index < slot_end)]
        if slot_data.empty:
            return "unknown"

        # Simple rule: if total precipitation > threshold -> rainy
        if slot_data['prcp'].sum() > 1.0:
            return "rainy"

        # Average temperature
        avg_temp = slot_data['temp'].mean()
        if avg_temp > 20:
            return "sunny"
        else:
            return "cloudy"

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
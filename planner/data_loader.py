from pathlib import Path

import pandas as pd
from shapely.geometry import Point
from .sights import Sight #p

'''def load_sights_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    sights = []
    for _, row in df.iterrows():
        # Defensive: check if columns exist
        lat = row['latitude'] if 'latitude' in df.columns else row.get('lat', None)
        lon = row['longitude'] if 'longitude' in df.columns else row.get('lon', None)
        if lat is None or lon is None:
            continue  # Skip invalid rows

        point = Point(lon, lat)  # Point(longitude, latitude)

        weather_suitability = row['weather_suitability']
        if pd.isna(weather_suitability):
            weather_suitability = []
        else:
            weather_suitability = weather_suitability.split('|')

        description = row['description'] if 'description' in df.columns else ''

        sight = Sight(
            name=row['name'],
            location=point,
            category=row['category'],
            weather_suitability=weather_suitability,
            description=description
        )
        sights.append(sight)
    return sights'''
import pandas as pd
from .sights import Sight #p
from shapely.geometry import Point

def load_sights_from_csv(path):
    df = pd.read_csv(path)

    sights = []
    for _, row in df.iterrows():
        try:
            name = str(row["name"]) if pd.notna(row["name"]) else "Unnamed Sight"
            category = str(row["category"]) if pd.notna(row["category"]) else "unknown"
            description = str(row["description"]) if pd.notna(row.get("description", "")) else ""
            # Defensive: check if columns exist
            lat = row['latitude'] if 'latitude' in df.columns else row.get('lat', None)
            lon = row['longitude'] if 'longitude' in df.columns else row.get('lon', None)
            if lat is None or lon is None:
                continue  # Skip invalid rows
            location = Point(lon, lat)

            weather = row.get("weather_suitability", "any")
            if isinstance(weather, str):
                weather_suitability = [w.strip() for w in weather.split(",")]
            else:
                weather_suitability = ["any"]

            sights.append(Sight(
                name=name,
                category=category,
                description=description,
                location=location,
                weather_suitability=weather_suitability
            ))
        except Exception as e:
            print(f"⚠️ Skipping bad row: {row.to_dict()} ({e})")
    return sights


def save_sights_to_csv(sights, csv_path: Path, allow_overwrite_recommendations=False):
    if "sights_" in csv_path.name and not allow_overwrite_recommendations:
        raise ValueError(f"🚫 Refusing to overwrite recommended file: {csv_path}")

    if not sights:
        print(f"⚠️ Not saving: zero sights to write.")
        return

    data = [{
        'name': s.name,
        'longitude': s.location.x,
        'latitude': s.location.y,
        'category': s.category,
        'weather_suitability': '|'.join(s.weather_suitability),
        'description': s.description
    } for s in sights]

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved {len(sights)} sights to {csv_path}")


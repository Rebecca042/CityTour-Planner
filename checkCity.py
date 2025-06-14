from shapely.geometry import Point

# Example call to fetch_osm_sights
# Coordinates for Sydney Opera House: -33.856784, 151.215297 (latitude, longitude)
# So, for shapely.Point(lon, lat): Point(151.215297, -33.856784)
from planner.osm import fetch_osm_sights

sydney_point = Point(151.215297, -33.856784)

# Try very broad tags and a larger radius to ensure some results
broad_tags = {
    "amenity": True, # Matches any amenity
    "tourism": True, # Matches any tourism feature
    "leisure": True, # Matches any leisure feature
    "shop": True # Matches any shop
}

# Fetch sights with refresh=True to clear cache and force a new fetch
sights_found = fetch_osm_sights(
    location=sydney_point,
    tags=broad_tags,
    refresh=True, # Set to True to force a fresh fetch
    radius_meters=1000 # Search within 1000 meters (1 km)
)

if sights_found:
    print(f"Found {len(sights_found)} sights around Sydney Opera House:")
    for sight in sights_found[:5]: # Print first 5 for brevity
        print(f"- {sight.name} ({sight.category}) at ({sight.location.y:.4f}, {sight.location.x:.4f})")
else:
    print("Still no sights found with these parameters. Double-check coordinates, radius, and tags.")

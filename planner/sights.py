from dataclasses import dataclass
import json
from typing import List
import folium
import geopandas as gpd
from shapely.geometry import Point
from .visualize import visualize_sights_on_map  #p



@dataclass(frozen=True)
class Sight:
    name: str
    location: Point
    category: str
    weather_suitability: List[str]
    description: str = ""
    def __repr__(self):
        return f"Sight(name={self.name}, category={self.category}, location={self.location})"
    def __eq__(self, other):
        if not isinstance(other, Sight):
            return False
        return self.name == other.name  # Or some unique ID

    def __hash__(self):
        return hash(self.name)  # Or some unique ID

# Sample Sight objects (Paris sights)
sights = [
    Sight(name="Louvre Museum", location=Point(2.3376, 48.8606), category="museum", weather_suitability="indoor",
          description="A world-famous art museum in Paris."),
    Sight(name="Eiffel Tower", location=Point(2.2945, 48.8584), category="monument", weather_suitability="outdoor",
          description="An iconic symbol of Paris."),
    Sight(name="Café de Flore", location=Point(2.3336, 48.8545), category="café", weather_suitability="sunny",
          description="A historic and trendy café in Paris."),
]

# Create the map visualization
visualize_sights_on_map(sights)

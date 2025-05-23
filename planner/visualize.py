import folium


def get_icon_by_weather(weather):
    if weather == "sunny":
        return folium.Icon(color="green", icon="sun-o")
    elif weather == "indoor":
        return folium.Icon(color="red", icon="home")
    else:  # Default to blue for outdoor
        return folium.Icon(color="blue", icon="cloud")


def visualize_sights_on_map(sights):
    map_center = [48.8566, 2.3522]  # Default to Paris
    tourist_map = folium.Map(location=map_center, zoom_start=12)

    for sight in sights:
        folium.Marker(
            location=[sight.location.y, sight.location.x],
            popup=f"<b>{sight.name}</b><br>{sight.category}<br>{sight.description}<br>Weather: {sight.weather_suitability}",
            icon=get_icon_by_weather(sight.weather_suitability)
        ).add_to(tourist_map)

    tourist_map.save("tourist_sights_map.html")
    print("Map has been saved as tourist_sights_map.html. Open it in your browser to view the interactive map!")
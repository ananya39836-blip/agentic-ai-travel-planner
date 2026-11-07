"""
Geocoding coordinates and WMO weather condition mappings for Indian cities.
"""

CITY_COORDINATES = {
    "Delhi": {"latitude": 28.6139, "longitude": 77.2090},
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "Bangalore": {"latitude": 12.9716, "longitude": 77.5946},
    "Goa": {"latitude": 15.2993, "longitude": 74.1240},
    "Jaipur": {"latitude": 26.9124, "longitude": 75.7873},
    "Kolkata": {"latitude": 22.5726, "longitude": 88.3639},
    "Chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "Hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
}

WMO_WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain ⛈️",
    71: "Slight snow ❄️",
    73: "Moderate snow ❄️",
    75: "Heavy snow ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    95: "Thunderstorm ⚡",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

def get_city_coords(city: str):
    """Return latitude and longitude for a given city name (case-insensitive)."""
    if not city:
        return None
    city_normalized = city.strip().capitalize()
    for name, coords in CITY_COORDINATES.items():
        if name.lower() == city.strip().lower():
            return coords
    return None

def interpret_weather_code(code: int) -> str:
    """Map WMO numeric weather code to readable description."""
    return WMO_WEATHER_CODES.get(code, "Variable conditions 🌤️")

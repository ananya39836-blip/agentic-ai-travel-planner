"""
Weather Lookup Tool: Fetches live daily weather forecasts using Open-Meteo API.
"""

import urllib.request
import json
from typing import Dict, Any, Optional
from ..utils.geocoding import get_city_coords, interpret_weather_code

def get_weather_forecast(city: str, days: int = 7) -> Dict[str, Any]:
    """
    Get live daily weather forecast for a specified city using Open-Meteo.
    
    Args:
        city: City name (e.g., 'Goa', 'Delhi', 'Jaipur')
        days: Number of forecast days to return (1-7)
        
    Returns:
        Dictionary containing city, coordinates, and list of daily forecast objects.
    """
    coords = get_city_coords(city)
    if not coords:
        return {
            "success": False,
            "error": f"City '{city}' not found in known coordinates registry.",
            "forecast": []
        }
        
    lat = coords["latitude"]
    lon = coords["longitude"]
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    )
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
        daily = data.get("daily", {})
        dates = daily.get("time", [])[:days]
        max_temps = daily.get("temperature_2m_max", [])[:days]
        min_temps = daily.get("temperature_2m_min", [])[:days]
        codes = daily.get("weathercode", [])[:days]
        
        forecast_list = []
        for i in range(len(dates)):
            wcode = codes[i] if i < len(codes) else 0
            cond = interpret_weather_code(wcode)
            forecast_list.append({
                "day_index": i + 1,
                "date": dates[i],
                "max_temp_c": max_temps[i] if i < len(max_temps) else None,
                "min_temp_c": min_temps[i] if i < len(min_temps) else None,
                "condition": cond,
                "summary": f"{cond} (High: {max_temps[i]}°C, Low: {min_temps[i]}°C)"
            })
            
        return {
            "success": True,
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "forecast": forecast_list
        }
    except Exception as e:
        # Graceful fallback with seasonal simulated estimates if offline
        fallback_forecast = [
            {
                "day_index": i + 1,
                "date": f"Day {i + 1}",
                "max_temp_c": 31.0 - i,
                "min_temp_c": 22.0,
                "condition": "Pleasant & Clear ☀️",
                "summary": f"Pleasant & Clear ☀️ (Approx High: {31-i}°C, Low: 22°C)"
            }
            for i in range(days)
        ]
        return {
            "success": False,
            "warning": f"Weather API request failed ({str(e)}). Provided seasonal estimate fallback.",
            "city": city,
            "forecast": fallback_forecast
        }

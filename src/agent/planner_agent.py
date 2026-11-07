"""
Agentic Travel Planner Engine.
Supports LangChain agent orchestration as well as autonomous multi-step reasoning.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from ..tools.flight_tool import search_flights
from ..tools.hotel_tool import search_hotels
from ..tools.places_tool import search_places
from ..tools.weather_tool import get_weather_forecast
from ..tools.budget_tool import estimate_trip_budget
from ..database.db_manager import DatabaseManager

class TravelPlannerAgent:
    """
    Autonomous travel planning agent that coordinates tools to create comprehensive itineraries.
    """
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.llm = self._init_llm_if_available()

    def _init_llm_if_available(self):
        """Initialize LangChain LLM if credentials and libraries exist."""
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            # Check for Google Gemini
            if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                from langchain_google_genai import ChatGoogleGenerativeAI
                key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=key, temperature=0.3)
            # Check for OpenAI
            if os.getenv("OPENAI_API_KEY"):
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        except Exception:
            pass
        return None

    def plan_trip(
        self,
        source: str,
        destination: str,
        num_days: int = 3,
        num_travelers: int = 1,
        min_hotel_stars: int = 3,
        max_hotel_price: Optional[int] = None,
        hotel_amenities: Optional[List[str]] = None,
        preferred_place_types: Optional[List[str]] = None,
        flight_preference: str = "price",
        is_roundtrip: bool = True,
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """
        Execute multi-step agentic planning workflow.
        """
        # Step 0: Record Search Query in SQLite
        search_id = self.db.save_search(
            source=source,
            destination=destination,
            num_days=num_days,
            num_travelers=num_travelers,
            raw_query=raw_query or f"Trip from {source} to {destination} for {num_days} days"
        )
        
        reasoning_log = []
        
        # Step 1: Tool Execution - Flight Search
        reasoning_log.append(f"Searching flights from {source} to {destination} prioritized by {flight_preference}...")
        flights = search_flights(source=source, destination=destination, sort_by=flight_preference, max_results=3)
        if not flights:
            # Fallback search if exact pair not found
            selected_flight = {
                "flight_id": "N/A",
                "airline": "Direct Flight / Inter-city Express",
                "from": source,
                "to": destination,
                "price": 3500,
                "duration_str": "2h 15m",
                "departure_time": "10:00 AM",
                "arrival_time": "12:15 PM"
            }
            reasoning_log.append(f"No direct flight found in dataset between {source} and {destination}; standard transit cost applied.")
        else:
            selected_flight = flights[0]
            reasoning_log.append(f"Selected {selected_flight['airline']} flight ({selected_flight.get('flight_id', '')}) at ₹{selected_flight['price']}.")

        # Step 2: Tool Execution - Hotel Recommendation
        reasoning_log.append(f"Searching {min_hotel_stars}★+ hotels in {destination} with amenities {hotel_amenities or []}...")
        hotels = search_hotels(
            city=destination,
            min_stars=min_hotel_stars,
            max_price=max_hotel_price,
            required_amenities=hotel_amenities,
            sort_by="rating",
            max_results=3
        )
        if not hotels:
            # Relax criteria if strict filter yields 0
            hotels = search_hotels(city=destination, min_stars=2, max_results=3)
            
        if hotels:
            selected_hotel = hotels[0]
            reasoning_log.append(f"Selected {selected_hotel['name']} ({selected_hotel['stars']}★) at ₹{selected_hotel['price_per_night']}/night.")
        else:
            selected_hotel = {
                "hotel_id": "HOT_DEFAULT",
                "name": f"Comfort Premier Stay {destination}",
                "city": destination,
                "stars": 3,
                "price_per_night": 2800,
                "amenities": ["wifi", "breakfast"]
            }
            reasoning_log.append("Default boutique hotel selected.")

        # Step 3: Tool Execution - Weather Forecast
        reasoning_log.append(f"Querying Open-Meteo live API for weather forecast in {destination}...")
        weather_res = get_weather_forecast(city=destination, days=num_days)
        weather_forecast = weather_res.get("forecast", [])
        reasoning_log.append(f"Retrieved {len(weather_forecast)} days of live weather predictions.")

        # Step 4: Tool Execution - Places Discovery & Daily Scheduling
        reasoning_log.append(f"Discovering attractions in {destination} matching preferences {preferred_place_types or 'all'}...")
        all_places = []
        if preferred_place_types:
            for ptype in preferred_place_types:
                pts = search_places(city=destination, place_type=ptype, min_rating=3.8, limit=5)
                all_places.extend(pts)
        if not all_places:
            all_places = search_places(city=destination, min_rating=4.0, limit=15)
        if not all_places:
            all_places = search_places(city=destination, min_rating=0.0, limit=15)

        # Remove duplicates
        seen_ids = set()
        unique_places = []
        for p in all_places:
            pid = p.get("place_id") or p.get("name")
            if pid not in seen_ids:
                seen_ids.add(pid)
                unique_places.append(p)

        # Distribute into Day-Wise Itinerary
        daywise_itinerary = []
        places_per_day = 2
        for day_idx in range(1, num_days + 1):
            day_weather = weather_forecast[day_idx - 1] if day_idx - 1 < len(weather_forecast) else {"condition": "Pleasant 🌤️"}
            cond_str = day_weather.get("condition", "Clear ☀️")
            
            # Select 2 places for this day
            p_start = (day_idx - 1) * places_per_day
            day_places = unique_places[p_start : p_start + places_per_day]
            
            p1_name = day_places[0]["name"] if len(day_places) > 0 else f"{destination} City Exploration"
            p1_type = day_places[0].get("type", "sightseeing") if len(day_places) > 0 else "attraction"
            p2_name = day_places[1]["name"] if len(day_places) > 1 else f"Local Market & Cultural Walk"
            p2_type = day_places[1].get("type", "market") if len(day_places) > 1 else "cultural"

            theme = f"Discovery & {p1_type.capitalize()}" if day_idx == 1 else (f"Adventure & {p2_type.capitalize()}" if day_idx == 2 else "Leisure & Culture")
            
            daywise_itinerary.append({
                "day": day_idx,
                "theme": theme,
                "weather_summary": cond_str,
                "morning": f"Morning check-in / breakfast. Visit {p1_name} ({p1_type.title()}) for scenic exploration.",
                "afternoon": f"Lunch sampling local delicacies followed by sightseeing at {p2_name}.",
                "evening": f"Sunset stroll, local cafe dinner, and cultural evening in {destination}.",
                "places_visited": [p["name"] for p in day_places] if day_places else [p1_name, p2_name]
            })
            
        reasoning_log.append(f"Assembled realistic {num_days}-day itinerary balanced across morning, afternoon, and evening.")

        # Step 5: Tool Execution - Budget Estimation
        flight_cost = selected_flight.get("price", 3500)
        hotel_cost = selected_hotel.get("price_per_night", 2500)
        
        budget = estimate_trip_budget(
            flight_cost_per_person=flight_cost,
            hotel_price_per_night=hotel_cost,
            num_days=num_days,
            num_travelers=num_travelers,
            is_roundtrip=is_roundtrip
        )
        reasoning_log.append(f"Computed total budget: ₹{budget['grand_total']} (Flights: ₹{budget['breakdown']['flight_expense']}, Hotel: ₹{budget['breakdown']['hotel_expense']}, Local: ₹{budget['breakdown']['local_food_and_transit']}).")

        # Compile Trip Title and Justification
        title = f"Your {num_days}-Day Trip to {destination}"
        justification = (
            f"Selected {selected_flight.get('airline', 'Flight')} for the best departure-to-fare value. "
            f"Booked {selected_hotel['name']} ({selected_hotel['stars']}★) providing high guest satisfaction with amenities. "
            f"Itinerary paced across {len(unique_places)} top attractions tailored to current weather conditions."
        )

        full_plan = {
            "search_id": search_id,
            "title": title,
            "source_city": source,
            "destination_city": destination,
            "num_days": num_days,
            "num_travelers": num_travelers,
            "flight": selected_flight,
            "hotel": selected_hotel,
            "weather": weather_forecast,
            "itinerary": daywise_itinerary,
            "budget": budget,
            "reasoning": justification,
            "reasoning_steps": reasoning_log
        }

        # Step 6: Save Complete Itinerary to SQLite
        itinerary_id = self.db.save_itinerary(
            search_id=search_id,
            destination=destination,
            title=title,
            total_days=num_days,
            total_cost=budget["grand_total"],
            flight_data=selected_flight,
            hotel_data=selected_hotel,
            daywise_data=daywise_itinerary,
            weather_data=weather_forecast,
            budget_data=budget,
            reasoning=justification
        )
        full_plan["itinerary_id"] = itinerary_id

        return full_plan

    def format_plan_as_markdown(self, plan: Dict[str, Any]) -> str:
        """Render itinerary as structured markdown according to capstone format."""
        flight = plan["flight"]
        hotel = plan["hotel"]
        budget = plan["budget"]
        breakdown = budget["breakdown"]
        
        md = []
        md.append(f"### {plan['title']}")
        md.append(f"**Route**: {plan['source_city']} ➔ {plan['destination_city']} | **Travelers**: {plan['num_travelers']} | **Duration**: {plan['num_days']} Days\n")
        
        md.append("#### ✈️ Flight Selected:")
        dep = flight.get('departure_time', 'Morning')
        arr = flight.get('arrival_time', '')
        time_info = f"Departs {flight.get('from', plan['source_city'])} at {dep}" + (f", Arrives at {arr}" if arr else "")
        md.append(f"- **{flight.get('airline', 'Airline')}** (₹{flight.get('price', 0):,}) – {time_info}\n")
        
        md.append("#### 🏨 Hotel Recommendation:")
        amenities_str = ", ".join(hotel.get('amenities', []))
        md.append(f"- **{hotel.get('name', 'Hotel')}** (₹{hotel.get('price_per_night', 0):,}/night, {hotel.get('stars', 3)}-star)")
        if amenities_str:
            md.append(f"  *Amenities: {amenities_str}*\n")
        else:
            md.append("")
            
        md.append("#### ☀️ Weather Outlook:")
        for w in plan.get("weather", []):
            md.append(f"- **Day {w.get('day_index', '')}**: {w.get('summary', w.get('condition', 'Pleasant'))}")
        md.append("")
        
        md.append("#### 🗺️ Day-Wise Itinerary:")
        for day in plan.get("itinerary", []):
            md.append(f"##### Day {day['day']}: {day['theme']} ({day.get('weather_summary', 'Sunny')})")
            md.append(f"- **Morning**: {day['morning']}")
            md.append(f"- **Afternoon**: {day['afternoon']}")
            md.append(f"- **Evening**: {day['evening']}")
            if day.get("places_visited"):
                md.append(f"- *Highlights*: {', '.join(day['places_visited'])}\n")
                
        md.append("#### 💰 Estimated Total Budget:")
        md.append(f"- Flight: ₹{breakdown.get('flight_expense', 0):,}")
        md.append(f"- Hotel ({budget.get('num_nights', 1)} nights): ₹{breakdown.get('hotel_expense', 0):,}")
        md.append(f"- Food & Travel: ₹{breakdown.get('local_food_and_transit', 0):,}")
        md.append(f"- Contingency / Buffer: ₹{breakdown.get('contingency_buffer', 0):,}")
        md.append("-------------------------------------")
        md.append(f"**Total Cost: ₹{budget.get('grand_total', 0):,}**\n")
        
        md.append("#### 💡 Agent Reasoning & Selection Logic:")
        md.append(f"{plan.get('reasoning', '')}\n")
        
        return "\n".join(md)

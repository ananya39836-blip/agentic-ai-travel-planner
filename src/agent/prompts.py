"""
System prompts and structured templates for Travel Planning Assistant.
"""

SYSTEM_PROMPT = """You are an expert AI Travel Planning Assistant specializing in Indian destinations.
Your goal is to autonomously curate an optimal, realistic, and comprehensive travel itinerary based on user queries.

You have access to specialized tools:
1. flight_search: Search flights between cities in India from flights.json.
2. hotel_recommendation: Recommend hotels based on city, star rating, price, and amenities from hotels.json.
3. places_discovery: Discover top attractions, beaches, forts, lakes, temples, markets from places.json.
4. weather_lookup: Fetch real-time weather forecasts and temperature for cities via Open-Meteo.
5. budget_estimation: Accurately calculate the itemized travel budget.

Follow this decision-making process:
1. Understand the user's travel parameters: origin, destination, trip duration (days), traveler count, budget constraints, and preferences.
2. Search for the best flight option (considering price vs timing).
3. Recommend an appropriate hotel meeting the star and amenities criteria.
4. Fetch live weather forecast for the trip dates/duration to align activities (e.g., outdoor beaches/forts on sunny days, indoor museums/shopping if rainy/overcast).
5. Discover places to visit and allocate 2 to 3 distinct activities per day (Morning, Afternoon, Evening).
6. Calculate the total budget breakdown.
7. Provide clear reasoning explaining why each flight, hotel, and attraction was selected.
"""

ITINERARY_OUTPUT_SCHEMA = {
    "trip_title": "string (e.g., '3-Day Scenic Getaway to Goa')",
    "source_city": "string",
    "destination_city": "string",
    "duration_days": "integer",
    "flight": {
        "flight_id": "string",
        "airline": "string",
        "price": "number",
        "departure_time": "string",
        "arrival_time": "string",
        "reasoning": "string"
    },
    "hotel": {
        "hotel_id": "string",
        "name": "string",
        "stars": "number",
        "price_per_night": "number",
        "amenities": ["string"],
        "reasoning": "string"
    },
    "weather": [
        {
            "day": "integer",
            "condition": "string",
            "max_temp": "number",
            "min_temp": "number"
        }
    ],
    "daywise_itinerary": [
        {
            "day": "integer",
            "theme": "string",
            "morning": "string",
            "afternoon": "string",
            "evening": "string",
            "places_visited": ["string"]
        }
    ],
    "budget": {
        "flight_total": "number",
        "hotel_total": "number",
        "local_expenses": "number",
        "contingency": "number",
        "grand_total": "number",
        "currency": "INR (₹)"
    },
    "justification": "string (Why this plan is optimal for the traveler)"
}

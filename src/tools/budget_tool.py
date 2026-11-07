"""
Budget Estimation Tool: Sums flights, accommodation, and per-day local expenses.
"""

from typing import Dict, Any

def estimate_trip_budget(
    flight_cost_per_person: float,
    hotel_price_per_night: float,
    num_days: int,
    num_travelers: int = 1,
    is_roundtrip: bool = False,
    daily_food_and_transit_per_person: float = 1250.0,
    contingency_percent: float = 10.0
) -> Dict[str, Any]:
    """
    Calculate an itemized trip budget breakdown.
    
    Args:
        flight_cost_per_person: One-way flight price per traveler
        hotel_price_per_night: Price per room per night
        num_days: Total days of trip (nights = days - 1 or at least 1)
        num_travelers: Number of people traveling
        is_roundtrip: True if user wants flight cost doubled for return leg
        daily_food_and_transit_per_person: Estimated daily local expense per traveler
        contingency_percent: Emergency/miscellaneous buffer percentage
        
    Returns:
        Itemized budget breakdown with subtotals and grand total.
    """
    num_nights = max(1, num_days - 1)
    # Assume 1 room per 2 travelers
    num_rooms = max(1, (num_travelers + 1) // 2)
    
    flight_multiplier = 2 if is_roundtrip else 1
    total_flight = flight_cost_per_person * flight_multiplier * num_travelers
    total_hotel = hotel_price_per_night * num_nights * num_rooms
    total_local = daily_food_and_transit_per_person * num_days * num_travelers
    
    subtotal = total_flight + total_hotel + total_local
    contingency_buffer = (subtotal * contingency_percent) / 100.0
    grand_total = subtotal + contingency_buffer
    
    return {
        "num_days": num_days,
        "num_nights": num_nights,
        "num_travelers": num_travelers,
        "is_roundtrip": is_roundtrip,
        "breakdown": {
            "flight_expense": round(total_flight, 2),
            "hotel_expense": round(total_hotel, 2),
            "local_food_and_transit": round(total_local, 2),
            "contingency_buffer": round(contingency_buffer, 2)
        },
        "subtotal": round(subtotal, 2),
        "grand_total": round(grand_total, 2),
        "currency": "INR (₹)"
    }

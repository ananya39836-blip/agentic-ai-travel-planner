"""
Hotel Recommendation Tool: Reads and filters hotels.json dataset.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "hotels.json"

def search_hotels(
    city: str,
    min_stars: int = 1,
    max_price: Optional[int] = None,
    required_amenities: Optional[List[str]] = None,
    sort_by: str = "rating",
    max_results: int = 5,
    data_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search and recommend hotels in a given city based on preferences.
    
    Args:
        city: Destination city name (e.g., 'Goa', 'Delhi')
        min_stars: Minimum star rating (1 to 5)
        max_price: Maximum allowed price per night in INR
        required_amenities: List of amenities (e.g. ['wifi', 'pool'])
        sort_by: Sorting preference ('rating' for highest stars/quality, 'price' for lowest cost)
        max_results: Maximum number of hotels to return
        data_path: Optional override path to hotels.json
    
    Returns:
        List of matching hotel dictionaries.
    """
    path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    if not path.exists():
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        hotels: List[Dict[str, Any]] = json.load(f)
        
    city_norm = city.strip().lower()
    req_amenities = [a.strip().lower() for a in required_amenities] if required_amenities else []
    
    matched = []
    for h in hotels:
        if h.get("city", "").strip().lower() != city_norm:
            continue
        if h.get("stars", 0) < min_stars:
            continue
        if max_price is not None and h.get("price_per_night", 0) > max_price:
            continue
        if req_amenities:
            hotel_amenities = [a.lower() for a in h.get("amenities", [])]
            if not all(ra in hotel_amenities for ra in req_amenities):
                continue
        matched.append(h)
        
    if sort_by == "price":
        matched.sort(key=lambda x: x.get("price_per_night", 999999))
    else:
        # Default: highest rating first, tie-break by price
        matched.sort(key=lambda x: (-x.get("stars", 0), x.get("price_per_night", 999999)))
        
    return matched[:max_results]

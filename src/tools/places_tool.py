"""
Places Discovery Tool: Reads and filters places.json dataset.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "places.json"

def search_places(
    city: str,
    place_type: Optional[str] = None,
    min_rating: float = 0.0,
    limit: int = 10,
    data_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Discover top tourist attractions and places to visit in a destination city.
    
    Args:
        city: City name (e.g., 'Goa', 'Jaipur', 'Delhi')
        place_type: Optional category filter (e.g., 'beach', 'fort', 'monument', 'temple', 'lake', 'market')
        min_rating: Minimum acceptable user rating (e.g. 4.0)
        limit: Maximum number of attractions to return
        data_path: Optional override path to places.json
        
    Returns:
        List of recommended places sorted by highest rating first.
    """
    path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    if not path.exists():
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        places: List[Dict[str, Any]] = json.load(f)
        
    city_norm = city.strip().lower()
    type_norm = place_type.strip().lower() if place_type else None
    
    matched = []
    for p in places:
        if p.get("city", "").strip().lower() != city_norm:
            continue
        if type_norm and p.get("type", "").strip().lower() != type_norm:
            continue
        if p.get("rating", 0.0) < min_rating:
            continue
        matched.append(p)
        
    # Sort by rating descending
    matched.sort(key=lambda x: x.get("rating", 0.0), reverse=True)
    return matched[:limit]

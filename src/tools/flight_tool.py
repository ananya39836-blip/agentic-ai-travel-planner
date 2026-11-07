"""
Flight Search Tool: Reads and filters flights.json dataset.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "flights.json"

def calculate_duration_minutes(departure_iso: str, arrival_iso: str) -> int:
    """Calculate flight duration in minutes."""
    try:
        dep = datetime.fromisoformat(departure_iso)
        arr = datetime.fromisoformat(arrival_iso)
        diff = arr - dep
        return int(diff.total_seconds() // 60)
    except Exception:
        return 0

def search_flights(
    source: str,
    destination: str,
    sort_by: str = "price",
    max_results: int = 5,
    data_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search flights from source to destination.
    
    Args:
        source: Departure city (e.g., 'Delhi', 'Mumbai')
        destination: Arrival city (e.g., 'Goa', 'Bangalore')
        sort_by: Criteria to rank flights ('price' for cheapest, 'duration' for fastest)
        max_results: Maximum number of flights to return
        data_path: Optional override path to flights.json
    
    Returns:
        List of matching flight dictionaries.
    """
    path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    if not path.exists():
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        flights: List[Dict[str, Any]] = json.load(f)
        
    src_norm = source.strip().lower()
    dst_norm = destination.strip().lower()
    
    matched = [
        f for f in flights
        if f.get("from", "").strip().lower() == src_norm and
           f.get("to", "").strip().lower() == dst_norm
    ]
    
    # Calculate duration for each flight
    for f in matched:
        duration_mins = calculate_duration_minutes(f.get("departure_time", ""), f.get("arrival_time", ""))
        hours = duration_mins // 60
        mins = duration_mins % 60
        f["duration_minutes"] = duration_mins
        f["duration_str"] = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        
    if sort_by == "duration":
        matched.sort(key=lambda x: x.get("duration_minutes", 9999))
    else:
        # Default: cheapest first
        matched.sort(key=lambda x: x.get("price", 999999))
        
    return matched[:max_results]

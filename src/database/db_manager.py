"""
SQLite Database Manager for Travel Planner.
Manages persistent records for searches, generated itineraries, and user feedback.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "travel_planner.db"

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._init_db()

    def _get_connection(self):
        """Create and yield a managed sqlite3 connection."""
        from contextlib import contextmanager
        @contextmanager
        def conn_ctx():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        return conn_ctx()

    def _init_db(self) -> None:
        """Create normalized tables and indexes if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Searches Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_city TEXT NOT NULL,
                    destination_city TEXT NOT NULL,
                    num_days INTEGER NOT NULL,
                    num_travelers INTEGER DEFAULT 1,
                    raw_query TEXT
                );
            """)
            
            # Itineraries Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itineraries (
                    itinerary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    destination_city TEXT NOT NULL,
                    trip_title TEXT NOT NULL,
                    total_days INTEGER NOT NULL,
                    total_cost REAL NOT NULL,
                    flight_json TEXT,
                    hotel_json TEXT,
                    daywise_json TEXT,
                    weather_json TEXT,
                    budget_json TEXT,
                    reasoning TEXT,
                    FOREIGN KEY (search_id) REFERENCES searches (search_id) ON DELETE SET NULL
                );
            """)
            
            # User Feedback Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    itinerary_id INTEGER NOT NULL,
                    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE
                );
            """)
            
            # Indexes for efficient queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_searches_dest ON searches(destination_city);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_itineraries_dest ON itineraries(destination_city);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_itinerary ON feedback(itinerary_id);")
            conn.commit()

    def save_search(self, source: str, destination: str, num_days: int, num_travelers: int = 1, raw_query: str = "") -> int:
        """Save a new travel search query."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO searches (source_city, destination_city, num_days, num_travelers, raw_query)
                VALUES (?, ?, ?, ?, ?)
            """, (source, destination, num_days, num_travelers, raw_query))
            conn.commit()
            return cursor.lastrowid

    def save_itinerary(
        self,
        search_id: Optional[int],
        destination: str,
        title: str,
        total_days: int,
        total_cost: float,
        flight_data: Dict[str, Any],
        hotel_data: Dict[str, Any],
        daywise_data: List[Dict[str, Any]],
        weather_data: List[Dict[str, Any]],
        budget_data: Dict[str, Any],
        reasoning: str = ""
    ) -> int:
        """Save a generated trip itinerary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO itineraries (
                    search_id, destination_city, trip_title, total_days,
                    total_cost, flight_json, hotel_json, daywise_json,
                    weather_json, budget_json, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search_id,
                destination,
                title,
                total_days,
                total_cost,
                json.dumps(flight_data),
                json.dumps(hotel_data),
                json.dumps(daywise_data),
                json.dumps(weather_data),
                json.dumps(budget_data),
                reasoning
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_itineraries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recently generated itineraries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT itinerary_id, created_at, destination_city, trip_title, total_days, total_cost, reasoning
                FROM itineraries
                ORDER BY itinerary_id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_itinerary_by_id(self, itinerary_id: int) -> Optional[Dict[str, Any]]:
        """Fetch complete itinerary details by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM itineraries WHERE itinerary_id = ?", (itinerary_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            for k in ["flight_json", "hotel_json", "daywise_json", "weather_json", "budget_json"]:
                if res.get(k):
                    try:
                        res[k] = json.loads(res[k])
                    except Exception:
                        pass
            return res

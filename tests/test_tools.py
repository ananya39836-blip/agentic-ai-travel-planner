"""
Unit tests for travel planner tools and database manager.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from src.tools.flight_tool import search_flights
from src.tools.hotel_tool import search_hotels
from src.tools.places_tool import search_places
from src.tools.weather_tool import get_weather_forecast
from src.tools.budget_tool import estimate_trip_budget
from src.database.db_manager import DatabaseManager
from src.agent.planner_agent import TravelPlannerAgent

class TestTravelPlannerTools(unittest.TestCase):

    def test_search_flights(self):
        flights = search_flights("Hyderabad", "Delhi")
        self.assertIsInstance(flights, list)
        self.assertGreater(len(flights), 0)
        self.assertEqual(flights[0]["from"].lower(), "hyderabad")
        self.assertEqual(flights[0]["to"].lower(), "delhi")
        self.assertIn("price", flights[0])

    def test_search_hotels(self):
        hotels = search_hotels("Goa", min_stars=3)
        self.assertIsInstance(hotels, list)
        self.assertGreater(len(hotels), 0)
        self.assertEqual(hotels[0]["city"].lower(), "goa")
        self.assertGreaterEqual(hotels[0]["stars"], 3)

    def test_search_places(self):
        places = search_places("Goa", min_rating=4.0)
        self.assertIsInstance(places, list)
        self.assertGreater(len(places), 0)
        self.assertEqual(places[0]["city"].lower(), "goa")
        self.assertGreaterEqual(places[0]["rating"], 4.0)

    def test_weather_lookup(self):
        res = get_weather_forecast("Goa", days=3)
        self.assertTrue(res["success"] or "warning" in res)
        self.assertIn("forecast", res)
        self.assertGreater(len(res["forecast"]), 0)

    def test_budget_estimation(self):
        budget = estimate_trip_budget(
            flight_cost_per_person=4800,
            hotel_price_per_night=3200,
            num_days=3,
            num_travelers=1,
            is_roundtrip=False,
            daily_food_and_transit_per_person=1250,
            contingency_percent=0 # matching reference
        )
        # 1 flight (4800) + 2 nights hotel (6400) + 3 days food (3750) = 14950
        self.assertEqual(budget["breakdown"]["flight_expense"], 4800)
        self.assertEqual(budget["breakdown"]["hotel_expense"], 6400)
        self.assertEqual(budget["grand_total"], 14950)

    def test_agent_end_to_end(self):
        test_db_path = Path(__file__).resolve().parent / "test_planner.db"
        if test_db_path.exists():
            test_db_path.unlink()
        db = DatabaseManager(str(test_db_path))
        agent = TravelPlannerAgent(db_manager=db)
        
        plan = agent.plan_trip(
            source="Delhi",
            destination="Goa",
            num_days=3,
            num_travelers=1
        )
        self.assertIn("title", plan)
        self.assertIn("flight", plan)
        self.assertIn("hotel", plan)
        self.assertIn("itinerary", plan)
        self.assertEqual(len(plan["itinerary"]), 3)
        self.assertIn("budget", plan)
        self.assertIn("itinerary_id", plan)

        # Clean up safely on Windows
        del agent
        del db
        import gc
        gc.collect()
        try:
            if test_db_path.exists():
                test_db_path.unlink()
        except PermissionError:
            pass

if __name__ == "__main__":
    unittest.main()

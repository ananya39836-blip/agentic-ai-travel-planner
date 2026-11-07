# Agentic AI-Based Travel Planning Assistant Using LangChain

An intelligent, multi-tool autonomous travel planner built in Python with LangChain, Open-Meteo live weather data, SQLite database persistence, and an interactive Streamlit UI.

---

## 📌 Project Overview
Planning a trip involves balancing flights, hotels, attractions, live weather, transit times, and budgets. This project provides an autonomous AI agent capable of multi-step reasoning to curate personalized, optimized, and cost-effective travel itineraries for Indian destinations.

### Key Capabilities
- **Flight Search Tool**: Scans `flights.json` (30 flights across major hubs), filters by source/destination, and ranks by price or duration.
- **Hotel Recommendation Tool**: Filters `hotels.json` (40 hotels) by city, star rating (2★–5★), price limits, and amenities (`wifi`, `pool`, `spa`, `gym`, `breakfast`, `parking`).
- **Places Discovery Tool**: Discovers attractions from `places.json` (40 attractions across beaches, forts, lakes, temples, markets, monuments, parks) sorted by user ratings.
- **Live Weather Lookup Tool**: Connects to the free Open-Meteo API to fetch real-time 7-day temperature highs/lows and weather conditions without requiring an API key.
- **Budget Estimation Tool**: Automatically calculates flight costs, multi-night hotel stay, local food/transit expenses, and contingency buffer.
- **SQLite Database Persistence**: Normalized relational tables for storing searches, generated itineraries, and user feedback.
- **Streamlit Interactive UI**: Dual-mode interface (Guided Wizard Form + Natural Language Chat) with cards, weather badges, and one-click Markdown/JSON exports.

---

## 🗂️ Project Directory Structure

```
travel_planner_agent/
│
├── data/
│   ├── flights.json          # Curated flight records between 8 major Indian cities
│   ├── hotels.json           # Hotel directory with amenities, star ratings, and prices
│   └── places.json           # Tourist attractions with categories and review ratings
│
├── src/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── flight_tool.py    # Flight search and duration calculation
│   │   ├── hotel_tool.py     # Hotel filtering by rating/amenities/budget
│   │   ├── places_tool.py    # POI discovery and curation
│   │   ├── weather_tool.py   # Open-Meteo live API integration
│   │   └── budget_tool.py    # Comprehensive trip expense breakdown
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── planner_agent.py  # Multi-step Agent reasoning & decision engine
│   │   └── prompts.py        # System instructions & output schemas
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py     # SQLite schema, indexing, and CRUD methods
│   └── utils/
│       ├── __init__.py
│       └── geocoding.py      # City coordinate registry & WMO weather mappings
│
├── tests/
│   └── test_tools.py         # Comprehensive unit and integration test suite
│
├── app.py                    # Streamlit web application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Set Active Workspace
It is recommended to set this directory as your active workspace:
```
C:\Users\HP\.gemini\antigravity\scratch\travel_planner_agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Unit Tests
Verify all tools, live APIs, and the database manager:
```bash
python tests/test_tools.py
```

### 4. Launch the Streamlit Web Application
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🌐 External APIs & Datasets
- **Open-Meteo API**: Live weather forecast endpoint (`https://api.open-meteo.com/v1/forecast`). Free, reliable, and requires no API key.
- **Datasets**: Downloaded from the project repository and stored in `data/`:
  - `flights.json`: 30 flights across Delhi, Mumbai, Bangalore, Goa, Jaipur, Kolkata, Chennai, Hyderabad.
  - `hotels.json`: 40 accommodations with price per night and amenities list.
  - `places.json`: 40 points of interest with ratings from 3.5 to 4.9.

---

## 📊 Sample Output Format

```markdown
### Your 3-Day Trip to Goa

✈️ **Flight Selected**:
- IndiGo (₹4,800) – Departs Delhi at 14:00

🏨 **Hotel Recommendation**:
- Sea View Resort (₹3,200/night, 4-star) – WiFi, Pool, Breakfast

☀️ **Weather Outlook**:
- Day 1: Sunny ☀️ (High: 31°C, Low: 22°C)
- Day 2: Partly Cloudy ⛅ (High: 30°C, Low: 22°C)
- Day 3: Clear Sky ☀️ (High: 29°C, Low: 21°C)

🗺️ **Day-Wise Itinerary**:
- Day 1: Arrival & check-in, visit Baga Beach, Candolim Market
- Day 2: Basilica of Bom Jesus, Old Goa Heritage Walk
- Day 3: Water sports at Calangute Beach, souvenir shopping

💰 **Estimated Total Budget**:
- Flight: ₹4,800
- Hotel: ₹6,400
- Food & Travel: ₹2,500
- Total Cost: ₹13,700

💡 **Agent Reasoning**:
- Selected IndiGo flight for lowest fare and convenient timing.
- Booked 4-star beachside stay with pool amenity.
```

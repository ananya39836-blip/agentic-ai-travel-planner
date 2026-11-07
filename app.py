"""
Streamlit Web Application: Agentic AI-Based Travel Planning Assistant Using LangChain.
"""

import os
import sys
from pathlib import Path
import json
import streamlit as st

# Setup sys.path so src imports work reliably
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.planner_agent import TravelPlannerAgent
from src.database.db_manager import DatabaseManager
from src.utils.geocoding import CITY_COORDINATES

# Set page config
st.set_page_config(
    page_title="AI Travel Planning Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
        background-color: #EFF6FF;
        color: #1D4ED8;
    }
    .metric-box {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 1px solid #BBF7D0;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()
if "agent" not in st.session_state:
    st.session_state.agent = TravelPlannerAgent(st.session_state.db)
if "current_plan" not in st.session_state:
    st.session_state.current_plan = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Configuration")
    
    # API key inputs
    api_choice = st.selectbox(
        "AI Reasoning Engine",
        ["Autonomous Tool Engine (Zero-Key)", "Google Gemini (LangChain)", "OpenAI (LangChain)"],
        index=0
    )
    
    if api_choice == "Google Gemini (LangChain)":
        gemini_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
    elif api_choice == "OpenAI (LangChain)":
        openai_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key

    st.markdown("---")
    st.subheader("📊 System & Datasets")
    st.markdown("✅ **Flights**: `flights.json` (30 flights)")
    st.markdown("✅ **Hotels**: `hotels.json` (40 hotels)")
    st.markdown("✅ **Attractions**: `places.json` (40 places)")
    st.markdown("✅ **Weather**: Open-Meteo Free API (Live)")
    st.markdown("✅ **Database**: SQLite (`travel_planner.db`)")
    
    st.markdown("---")
    st.subheader("📜 Recent Saved Itineraries")
    recent = st.session_state.db.get_recent_itineraries(limit=5)
    if recent:
        for item in recent:
            btn_label = f"📍 {item['destination_city']} ({item['total_days']}d) - ₹{int(item['total_cost']):,}"
            if st.button(btn_label, key=f"hist_{item['itinerary_id']}"):
                loaded = st.session_state.db.get_itinerary_by_id(item["itinerary_id"])
                if loaded:
                    st.session_state.current_plan = {
                        "title": loaded["trip_title"],
                        "source_city": "Saved Origin",
                        "destination_city": loaded["destination_city"],
                        "num_days": loaded["total_days"],
                        "num_travelers": 1,
                        "flight": loaded["flight_json"],
                        "hotel": loaded["hotel_json"],
                        "weather": loaded["weather_json"],
                        "itinerary": loaded["daywise_json"],
                        "budget": loaded["budget_json"],
                        "reasoning": loaded["reasoning"],
                        "reasoning_steps": ["Loaded from saved SQLite database archive."]
                    }
    else:
        st.caption("No saved itineraries yet.")

# Main Interface
st.markdown('<div class="main-title">✈️ Agentic AI Travel Planning Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by LangChain, Multi-Tool Reasoning & Live Open-Meteo Weather Data</div>', unsafe_allow_html=True)

cities_list = list(CITY_COORDINATES.keys())

tab_guided, tab_chat = st.tabs(["🎯 Guided Trip Planner", "💬 Natural Language Query"])

with tab_guided:
    with st.form("planner_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            source_city = st.selectbox("Origin City", cities_list, index=cities_list.index("Delhi") if "Delhi" in cities_list else 0)
        with col2:
            dest_city = st.selectbox("Destination City", cities_list, index=cities_list.index("Goa") if "Goa" in cities_list else 1)
        with col3:
            num_days = st.slider("Duration (Days)", min_value=1, max_value=7, value=3)
        with col4:
            num_travelers = st.number_input("Travelers", min_value=1, max_value=10, value=1)
            
        col_pref1, col_pref2, col_pref3 = st.columns(3)
        with col_pref1:
            min_stars = st.selectbox("Hotel Minimum Stars", [2, 3, 4, 5], index=1)
        with col_pref2:
            amenities = st.multiselect("Desired Amenities", ["wifi", "pool", "spa", "gym", "breakfast", "parking"], default=["wifi"])
        with col_pref3:
            place_types = st.multiselect("Attraction Preferences", ["beach", "fort", "lake", "market", "monument", "museum", "park", "temple"], default=["beach", "market"] if dest_city == "Goa" else ["monument", "market"])

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            flight_pref = st.radio("Flight Priority", ["Cheapest (price)", "Fastest (duration)"], horizontal=True)
            flight_sort = "price" if "Cheapest" in flight_pref else "duration"
        with col_opt2:
            is_roundtrip = st.checkbox("Include Return Flight in Budget", value=True)

        submitted = st.form_submit_button("🚀 Generate Optimized Itinerary", use_container_width=True)

    if submitted:
        if source_city == dest_city:
            st.error("Origin and Destination cities must be different!")
        else:
            with st.spinner("Agent reasoning in progress: searching flights, hotels, live weather & planning days..."):
                plan = st.session_state.agent.plan_trip(
                    source=source_city,
                    destination=dest_city,
                    num_days=num_days,
                    num_travelers=num_travelers,
                    min_hotel_stars=min_stars,
                    hotel_amenities=amenities,
                    preferred_place_types=place_types,
                    flight_preference=flight_sort,
                    is_roundtrip=is_roundtrip,
                    raw_query=f"Guided plan from {source_city} to {dest_city} for {num_days} days"
                )
                st.session_state.current_plan = plan
                st.success("Itinerary generated and archived to SQLite database!")

with tab_chat:
    st.info("💡 You can type natural language instructions like: *'Plan a 3-day budget trip from Mumbai to Goa for 2 travelers focusing on beaches and relaxation.'*")
    query_text = st.text_input("Enter your travel query:", placeholder="e.g. Plan a 4-day trip from Bangalore to Jaipur with 4-star hotels")
    chat_submit = st.button("Submit Query")
    
    if chat_submit and query_text:
        # Simple entity extraction from query text
        found_source = "Delhi"
        found_dest = "Goa"
        found_days = 3
        
        for c in cities_list:
            if f"from {c.lower()}" in query_text.lower():
                found_source = c
            elif f"to {c.lower()}" in query_text.lower():
                found_dest = c
            elif c.lower() in query_text.lower() and c != found_source:
                found_dest = c
                
        import re
        day_match = re.search(r'(\d+)\s*(?:-| )?day', query_text, re.IGNORECASE)
        if day_match:
            found_days = min(7, max(1, int(day_match.group(1))))
            
        with st.spinner(f"Agent analyzing prompt: planning trip from {found_source} to {found_dest} for {found_days} days..."):
            plan = st.session_state.agent.plan_trip(
                source=found_source,
                destination=found_dest,
                num_days=found_days,
                num_travelers=1,
                raw_query=query_text
            )
            st.session_state.current_plan = plan
            st.success(f"Trip to {found_dest} generated from prompt!")

# Render Results
if st.session_state.current_plan:
    plan = st.session_state.current_plan
    st.markdown("---")
    
    st.header(plan["title"])
    st.caption(f"Route: **{plan['source_city']}** ➔ **{plan['destination_city']}** | Travelers: **{plan['num_travelers']}** | Duration: **{plan['num_days']} Days**")
    
    # Top Row Cards: Flight & Hotel
    col_flight, col_hotel = st.columns(2)
    
    with col_flight:
        st.subheader("✈️ Flight Selected")
        f = plan["flight"]
        with st.container():
            st.markdown(f"**Airline**: {f.get('airline', 'Flight')}")
            st.markdown(f"**Flight ID**: `{f.get('flight_id', 'N/A')}`")
            st.markdown(f"**Departure**: {f.get('departure_time', 'Morning')}")
            st.markdown(f"**Arrival**: {f.get('arrival_time', 'Afternoon')}")
            st.markdown(f"**Fare per person**: ₹{f.get('price', 0):,}")
            if "duration_str" in f:
                st.markdown(f"**Duration**: {f['duration_str']}")
                
    with col_hotel:
        st.subheader("🏨 Hotel Recommendation")
        h = plan["hotel"]
        with st.container():
            st.markdown(f"**Hotel**: {h.get('name', 'Hotel')}")
            stars = "⭐" * int(h.get('stars', 3))
            st.markdown(f"**Rating**: {stars} ({h.get('stars', 3)}-star)")
            st.markdown(f"**Price per night**: ₹{h.get('price_per_night', 0):,}")
            amenities_badges = " ".join([f"`{a}`" for a in h.get("amenities", [])])
            st.markdown(f"**Amenities**: {amenities_badges}")

    # Weather Outlook
    st.markdown("---")
    st.subheader("☀️ Real-Time Weather Outlook (Open-Meteo)")
    weather_cols = st.columns(min(len(plan.get("weather", [])), 7) or 1)
    for idx, w in enumerate(plan.get("weather", [])[:7]):
        with weather_cols[idx]:
            st.markdown(f"**Day {w.get('day_index', idx + 1)}**")
            st.caption(w.get("date", f"Day {idx+1}"))
            st.markdown(f"### {w.get('max_temp_c', 30)}°C")
            st.caption(f"Low: {w.get('min_temp_c', 22)}°C")
            st.write(w.get("condition", "Sunny ☀️"))

    # Day-Wise Itinerary
    st.markdown("---")
    st.subheader("🗺️ Day-Wise Itinerary")
    for day in plan.get("itinerary", []):
        with st.expander(f"📍 Day {day['day']}: {day['theme']} - {day.get('weather_summary', 'Clear')}", expanded=True):
            col_m, col_a, col_e = st.columns(3)
            with col_m:
                st.markdown("**🌅 Morning**")
                st.write(day["morning"])
            with col_a:
                st.markdown("**☀️ Afternoon**")
                st.write(day["afternoon"])
            with col_e:
                st.markdown("**🌙 Evening**")
                st.write(day["evening"])
            if day.get("places_visited"):
                st.markdown(f"**Places Visited**: {', '.join(day['places_visited'])}")

    # Budget Breakdown
    st.markdown("---")
    st.subheader("💰 Estimated Total Budget")
    b = plan["budget"]
    bd = b["breakdown"]
    
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("✈️ Flights Total", f"₹{int(bd.get('flight_expense', 0)):,}")
    with b_col2:
        st.metric("🏨 Hotel Total", f"₹{int(bd.get('hotel_expense', 0)):,}")
    with b_col3:
        st.metric("🍽️ Meals & Local Transit", f"₹{int(bd.get('local_food_and_transit', 0)):,}")
    with b_col4:
        st.metric("🛡️ Contingency Buffer", f"₹{int(bd.get('contingency_buffer', 0)):,}")
        
    st.markdown(f"""
    <div class="metric-box">
        <h3 style="margin: 0; color: #166534;">Total Estimated Trip Cost: ₹{int(b.get('grand_total', 0)):,}</h3>
        <p style="margin: 0; color: #15803D; font-size: 0.9rem;">(Covers {b.get('num_travelers', 1)} traveler(s) for {b.get('num_days', 3)} days / {b.get('num_nights', 2)} nights)</p>
    </div>
    """, unsafe_allow_html=True)

    # Agent Reasoning Trace
    st.markdown("---")
    with st.expander("🧠 Autonomous Agent Reasoning & Selection Trace", expanded=False):
        st.write(f"**Primary Decision Justification**: {plan.get('reasoning', '')}")
        st.markdown("**Step-by-step Tool Calling Trace:**")
        for step in plan.get("reasoning_steps", []):
            st.markdown(f"- `{step}`")

    # Export & Downloads
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    md_text = st.session_state.agent.format_plan_as_markdown(plan)
    with col_dl1:
        st.download_button(
            label="📥 Download Markdown Summary (.md)",
            data=md_text,
            file_name=f"{plan['destination_city']}_itinerary.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        json_data = json.dumps(plan, indent=2)
        st.download_button(
            label="📥 Download Structured JSON (.json)",
            data=json_data,
            file_name=f"{plan['destination_city']}_itinerary.json",
            mime="application/json",
            use_container_width=True
        )

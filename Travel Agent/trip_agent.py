# travel_agent_final_fixed.py
import streamlit as st
import json, os, base64, time
from datetime import datetime, timedelta
from threading import Thread
from icalendar import Calendar, Event
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
MODEL = "grok-4"

# ============= SESSION STATE =============
for key in ["trip", "confirmed", "monitoring", "last_prices", "weather", "latest_prices"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key in ["trip","last_prices","weather","latest_prices"] else False

# Load saved trip
if os.path.exists("trip.json"):
    with open("trip.json") as f:
        data = json.load(f)
        st.session_state.trip = data.get("trip", {})
        st.session_state.confirmed = data.get("confirmed", bool(st.session_state.trip))

# ============= HELPERS =============
def save_trip():
    with open("trip.json", "w") as f:
        json.dump({"trip": st.session_state.trip, "confirmed": True}, f)

def create_ics():
    cal = Calendar()
    cal.add('prodid', '-//Grok Travel Agent//')
    e = Event()
    e.add('summary', f"✈️ Trip to {st.session_state.trip['destination_city']}")
    e.add('dtstart', datetime.fromisoformat(st.session_state.trip['departure_date']))
    end_date = st.session_state.trip.get('return_date') or st.session_state.trip['departure_date']
    e.add('dtend', datetime.fromisoformat(end_date) + timedelta(days=1))
    e.add('location', st.session_state.trip['destination_city'])
    cal.add_component(e)
    return f'data:text/calendar;base64,{base64.b64encode(cal.to_ical()).decode()}'

def google_links():
    t = st.session_state.trip
    dep = t.get('departure_airport_code', '')
    dest = t.get('destination_airport_code', '')
    return {
        "flights": f"https://www.google.com/travel/flights?q=Flights+from+{dep}+to+{dest}+on+{t['departure_date']}+return+{t.get('return_date','')}",
        "hotels": f"https://www.google.com/travel/hotels?q=Hotels+in+{t['destination_city'].replace(' ','+')}+check-in+{t['hotel_checkin']}+check-out+{t['hotel_checkout']}",
        "maps": f"https://www.google.com/maps/search/?api=1&query={t['destination_city'].replace(' ','+')}"
    }

# ============= MONITORING THREAD =============
def monitoring_loop():
    while st.session_state.monitoring:
        time.sleep(900)  # 15 minutes
        prompt = f"""Search live prices RIGHT NOW for this exact trip:
{json.dumps(st.session_state.trip, indent=2)}

Return ONLY valid JSON:
{{
  "flight_usd": 847,
  "airline": "Air France",
  "flight_link": "https://google.com/flights...",
  "hotel_name": "Shangri-La Paris",
  "hotel_total_usd": 3420,
  "hotel_link": "https://booking.com/..."
}}
"""
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You have real-time web access. Return ONLY valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            data = json.loads(resp.choices[0].message.content)
            st.session_state.latest_prices = data

            # Price drop detection
            if st.session_state.last_prices.get("flight") and data["flight_usd"] < st.session_state.last_prices["flight"] * 0.92:
                st.toast(f"FLIGHT PRICE DROP! ${st.session_state.last_prices['flight']} → ${data['flight_usd']}", icon="✈️")

            st.session_state.last_prices = {"flight": data["flight_usd"], "hotel": data["hotel_total_usd"]}
            st.rerun()
        except Exception as e:
            pass  # silent retry next cycle

if st.session_state.monitoring and not hasattr(st.session_state, "thread"):
    st.session_state.thread = Thread(target=monitoring_loop, daemon=True)
    st.session_state.thread.start()

# ============= UI =============
st.set_page_config(page_title="Grok Travel Agent", page_icon="✈️", layout="centered")
st.markdown("<h1 style='text-align:center;'>✈️ Grok Travel Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Tell me your trip — I’ll watch prices 24/7 and alert you on drops</p>", unsafe_allow_html=True)
st.divider()

# ——— STEP 1: Plan Trip ———
if not st.session_state.confirmed:
    prompt = st.chat_input("Where and when are you traveling? (e.g. Paris from Cincinnati, 3rd week Feb 2026, Tue–Sun)")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Planning your perfect trip..."):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{
                        "role": "system",
                        "content": """You are the best travel agent on Earth. Parse the user's request and return PERFECT JSON with these exact keys (nothing else):
{
  "departure_city": "Cincinnati",
  "departure_airport_code": "CVG",
  "destination_city": "Paris",
  "destination_airport_code": "CDG",
  "departure_date": "2026-02-17",
  "return_date": "2026-02-22",
  "adults": 1,
  "hotel_checkin": "2026-02-17",
  "hotel_checkout": "2026-02-22",
  "rooms": 1
}"""
                    }, {"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                try:
                    trip = json.loads(response.choices[0].message.content)
                    st.session_state.trip = trip
                    save_trip()

                    # Immediate weather forecast
                    wresp = client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role":"user", "content": f"7-day weather forecast for {trip['destination_city']} from {trip['hotel_checkin']} to {trip['hotel_checkout']}. Return JSON array of objects with date (YYYY-MM-DD), high_c, low_c, condition."}],
                        response_format={"type":"json_object"}
                    )
                    st.session_state.weather = json.loads(wresp.choices[0].message.content).get("forecast", [])

                    st.success("Trip perfectly understood!")
                    st.rerun()
                except Exception as e:
                    st.error("I need a bit more detail — try again!")

# ——— STEP 2: Confirmed Trip View ———
else:
    t = st.session_state.trip

    # Header
    st.success("✅ Trip Confirmed")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{t['departure_city']} ({t['departure_airport_code']}) → {t['destination_city']} ({t.get('destination_airport_code','')})")
        st.write(f"**Out:** {t['departure_date']} **Back:** {t.get('return_date','One-way')}  **Stay:** {t['hotel_checkin']} → {t['hotel_checkout']}")
    with col2:
        st.download_button("📅 Add to Calendar", create_ics(), f"Trip_to_{t['destination_city']}.ics", "text/calendar")

    # Links
    links = google_links()
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"[✈️ Google Flights]({links['flights']})")
    with col2: st.markdown(f"[🏨 Google Hotels]({links['hotels']})")
    with col3: st.markdown(f"[🗺️ Maps]({links['maps']})")

    # Weather Forecast
    if st.session_state.weather:
        st.markdown("### ☀️ Weather Forecast")
        weather_cols = st.columns(min(len(st.session_state.weather), 7))
        for i, day in enumerate(st.session_state.weather[:7]):
            with weather_cols[i]:
                st.metric(day.get("date", "—"), f"{day.get('high_c','?')}°C", f"{day.get('low_c','?')}°C")
                st.caption(day.get("condition", "—"))

    # Big Confirm & Start Button
    if not st.session_state.monitoring:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("**Confirm Trip & Start 24/7 Price Monitoring**", type="primary", use_container_width=True):
            st.session_state.monitoring = True
            st.balloons()
            st.rerun()
    else:
        st.success("🟢 Monitoring ACTIVE – checking every 15 minutes")
        if st.session_state.latest_prices:
            lp = st.session_state.latest_prices
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Best Flight Price", f"${lp.get('flight_usd',0):,}")
                st.markdown(f"**{lp.get('airline','')}**  [Book →]({lp.get('flight_link','')})")
            with col2:
                st.metric("Best Hotel Total", f"${lp.get('hotel_total_usd',0):,}")
                st.write(lp.get('hotel_name',''))
                st.markdown(f"[Book →]({lp.get('hotel_link','')})")

    if st.button("Start Over – Plan a New Trip"):
        for k in ["trip","confirmed","monitoring","last_prices","weather","latest_prices","thread"]:
            if k in st.session_state: del st.session_state[k]
        if os.path.exists("trip.json"): os.remove("trip.json")
        st.rerun()

st.divider()
st.caption("Powered by Grok-4 • Built with ❤️ by xAI")
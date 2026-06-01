"""
Tennis via TheSportsDB — trae próximos eventos del circuito ATP/WTA.
League IDs: ATP = 4438, WTA = 4439
"""
import requests
from datetime import datetime, timedelta
import pytz
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import TIMEZONE, MEXICO_BROADCAST

BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
MX_TZ = pytz.timezone(TIMEZONE)

TENNIS_LEAGUES = {
    "ATP Tour": "4438",
    "WTA Tour": "4439",
}


def _get(endpoint):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [Tennis] Error: {e}")
        return {}


def fetch_week_events():
    print("  Consultando Tennis...")
    today = datetime.now(MX_TZ).date()
    events = []

    for league_name, league_id in TENNIS_LEAGUES.items():
        data = _get(f"eventsnextleague.php?id={league_id}")
        raw = data.get("events") or []
        for e in raw:
            date_str = e.get("dateEvent", "")
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                continue
            if not (today <= event_date <= today + timedelta(days=7)):
                continue

            tournament = e.get("strLeague", league_name)
            # Solo mostrar si es Grand Slam o Masters relevante
            keywords = ["grand slam", "open", "masters", "wimbledon", "roland", "us open", "australian"]
            name_lower = (e.get("strEvent", "") + tournament).lower()
            if not any(k in name_lower for k in keywords):
                continue

            events.append({
                "sport": "Tenis",
                "league": tournament,
                "home": e.get("strHomeTeam", e.get("strEvent", "")),
                "away": e.get("strAwayTeam", ""),
                "date": event_date,
                "time_mx": "Ver horarios",
                "broadcast": MEXICO_BROADCAST.get("Tennis Grand Slam", "ESPN / Star+"),
                "favorite": False,
                "home_badge": "",
                "away_badge": "",
            })

    return events

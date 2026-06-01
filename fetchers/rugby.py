"""
Rugby via TheSportsDB.
Prioridad: Argentina (Pumas/Sevens) > competencias internacionales mayores.
"""
import requests
from datetime import datetime, timedelta
import pytz
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import TIMEZONE, MEXICO_BROADCAST

BASE = "https://www.thesportsdb.com/api/v1/json/3"
MX_TZ = pytz.timezone(TIMEZONE)

# League IDs TheSportsDB — rugby
RUGBY_LEAGUES = {
    "The Rugby Championship":       "4369",
    "Six Nations Championship":     "4368",
    "Rugby World Cup":              "4391",
    "World Rugby Sevens Series":    "4436",
    "Gallagher Premiership":        "4305",
    "United Rugby Championship":    "4322",
}


def _get(endpoint):
    try:
        r = requests.get(f"{BASE}/{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"    [Rugby] Error: {e}")
        return {}


def _utc_to_mx(date_str, time_str):
    if not date_str:
        return None, "TBD"
    try:
        dt_utc = datetime.strptime(f"{date_str} {time_str or '12:00:00'}", "%Y-%m-%d %H:%M:%S")
        dt_utc = pytz.utc.localize(dt_utc)
        dt_mx  = dt_utc.astimezone(MX_TZ)
        return dt_mx.date(), dt_mx.strftime("%H:%M")
    except Exception:
        return None, "TBD"


def fetch_week_events():
    print("    Rugby...")
    today = datetime.now(MX_TZ).date()
    events = []

    for league_name, league_id in RUGBY_LEAGUES.items():
        data = _get(f"eventsnextleague.php?id={league_id}")
        for e in (data.get("events") or []):
            date_str = e.get("dateEvent","")
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                continue
            if not (today <= event_date <= today + timedelta(days=7)):
                continue

            event_date_obj, time_mx = _utc_to_mx(date_str, e.get("strTime",""))

            home = e.get("strHomeTeam","")
            away = e.get("strAwayTeam","")

            events.append({
                "sport":      "Rugby",
                "league":     league_name,
                "home":       home,
                "away":       away,
                "date":       event_date,
                "time_mx":    time_mx,
                "broadcast":  MEXICO_BROADCAST.get("Rugby", "ESPN"),
                "favorite":   False,
                "note":       "",
                "home_badge": e.get("strHomeTeamBadge",""),
                "away_badge": e.get("strAwayTeamBadge",""),
            })

    return events

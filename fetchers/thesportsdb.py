import requests
from datetime import datetime, timedelta
import pytz
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FOOTBALL_LEAGUES, FAVORITE_TEAMS, MEXICO_BROADCAST, TIMEZONE

BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
MX_TZ = pytz.timezone(TIMEZONE)


def _get(endpoint):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [TheSportsDB] Error en {endpoint}: {e}")
        return {}


def _utc_to_mx(date_str, time_str):
    """Convierte fecha/hora UTC de la API a hora México."""
    if not date_str or not time_str:
        return None, None
    try:
        dt_utc = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_utc = pytz.utc.localize(dt_utc)
        dt_mx = dt_utc.astimezone(MX_TZ)
        return dt_mx.strftime("%H:%M"), dt_mx.strftime("%A %d/%m")
    except Exception:
        return time_str, date_str


def _is_favorite(home, away):
    for team in FAVORITE_TEAMS:
        if team.lower() in (home or "").lower() or team.lower() in (away or "").lower():
            return True
    return False


def _get_broadcast(league_name):
    for key, channel in MEXICO_BROADCAST.items():
        if key.lower() in league_name.lower():
            return channel
    return "ESPN / Star+"


def fetch_week_events(start_date=None):
    """Trae eventos de las ligas configuradas para los próximos 7 días."""
    if start_date is None:
        start_date = datetime.now(MX_TZ).date()

    all_events = []

    for league_name, league_id in FOOTBALL_LEAGUES.items():
        print(f"  Consultando {league_name}...")
        data = _get(f"eventsnextleague.php?id={league_id}")
        events = data.get("events") or []

        for e in events:
            event_date_str = e.get("dateEvent", "")
            try:
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except Exception:
                continue

            # Solo los próximos 7 días
            if not (start_date <= event_date <= start_date + timedelta(days=7)):
                continue

            time_mx, _ = _utc_to_mx(event_date_str, e.get("strTime", ""))

            all_events.append({
                "sport": "Fútbol",
                "league": league_name,
                "home": e.get("strHomeTeam", ""),
                "away": e.get("strAwayTeam", ""),
                "date": event_date,
                "time_mx": time_mx or "TBD",
                "broadcast": _get_broadcast(league_name),
                "favorite": _is_favorite(e.get("strHomeTeam"), e.get("strAwayTeam")),
                "home_badge": e.get("strHomeTeamBadge", ""),
                "away_badge": e.get("strAwayTeamBadge", ""),
            })

    return sorted(all_events, key=lambda x: (x["date"], x.get("time_mx", "")))


def fetch_today_events():
    today = datetime.now(MX_TZ).date()
    week = fetch_week_events(start_date=today)
    return [e for e in week if e["date"] == today]

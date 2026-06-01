"""
Fetcher principal usando la API pública de ESPN.
Cubre fútbol ARG/EUR, NBA, y detalles de transmisión.
No requiere API key.
"""
import requests
from datetime import datetime, timedelta
import pytz
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FAVORITE_TEAMS, MEXICO_BROADCAST, TIMEZONE

BASE = "https://site.api.espn.com/apis/site/v2/sports"
MX_TZ = pytz.timezone(TIMEZONE)

# (slug_ESPN, nombre_display, clave_broadcast_config)
FOOTBALL_SLUGS = [
    ("arg.1",                    "Argentine Primera División",   "Argentine Primera"),
    ("conmebol.libertadores",    "Copa Libertadores",            "Argentine Primera"),
    ("conmebol.sudamericana",    "Copa Sudamericana",            "Argentine Primera"),
    ("esp.1",                    "LaLiga",                       "LaLiga"),
    ("esp.copa_del_rey",         "Copa del Rey",                 "Copa del Rey"),
]

# IDs ESPN de equipos favoritos (fútbol ARG)
FAVORITE_TEAM_IDS = {
    "16": "River Plate",
    "5":  "Boca Juniors",
    "8":  "Estudiantes de La Plata",
}


def _get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"    [ESPN] Error {url}: {e}")
        return {}


def _utc_to_mx(date_str):
    """Convierte ISO date string UTC a hora México."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        dt_mx = dt.astimezone(MX_TZ)
        return dt_mx.date(), dt_mx.strftime("%H:%M"), dt_mx
    except Exception:
        return None, "TBD", None


def _is_favorite(competitors):
    for c in competitors:
        team_id = str(c.get("id", ""))
        name = c.get("team", {}).get("displayName", "")
        if team_id in FAVORITE_TEAM_IDS:
            return True
        for fav in FAVORITE_TEAMS:
            if fav.lower() in name.lower():
                return True
    return False


def _parse_broadcast(comps, default_key):
    """Extrae canal de transmisión o usa el default de config."""
    broadcasts = comps.get("broadcasts", [])
    if broadcasts:
        names = broadcasts[0].get("names", [])
        if names:
            return ", ".join(names)
    return MEXICO_BROADCAST.get(default_key, "ESPN / Star+")


def _parse_competition(event, sport_name, league_name, broadcast_key):
    """Normaliza un evento ESPN al formato interno."""
    date_str = event.get("date", "")
    event_date, time_mx, dt_mx = _utc_to_mx(date_str)
    if event_date is None:
        return None

    today = datetime.now(MX_TZ).date()
    if not (today <= event_date <= today + timedelta(days=7)):
        return None

    comps = event.get("competitions", [{}])[0]
    competitors = comps.get("competitors", [])
    names = [c.get("team", {}).get("displayName", c.get("athlete", {}).get("displayName", "")) for c in competitors]

    home = names[0] if len(names) > 0 else event.get("name", "")
    away = names[1] if len(names) > 1 else ""

    home_badge = ""
    away_badge = ""
    if len(competitors) >= 2:
        home_badge = competitors[0].get("team", {}).get("logo", "")
        away_badge = competitors[1].get("team", {}).get("logo", "")

    return {
        "sport": sport_name,
        "league": league_name,
        "home": home,
        "away": away,
        "date": event_date,
        "time_mx": time_mx,
        "broadcast": _parse_broadcast(comps, broadcast_key),
        "favorite": _is_favorite(competitors),
        "home_badge": home_badge,
        "away_badge": away_badge,
    }


def fetch_football_week():
    """Trae partidos de fútbol de los próximos 7 días."""
    all_events = []
    today = datetime.now(MX_TZ)

    for slug, league_name, broadcast_key in FOOTBALL_SLUGS:
        print(f"    {league_name}...")
        # ESPN scoreboard devuelve eventos del día; iterar días relevantes
        seen = set()
        for day_offset in range(8):
            date = today + timedelta(days=day_offset)
            data = _get(f"{BASE}/soccer/{slug}/scoreboard",
                        params={"dates": date.strftime("%Y%m%d")})
            for event in data.get("events", []):
                eid = event.get("id")
                if eid in seen:
                    continue
                seen.add(eid)
                evt = _parse_competition(event, "Fútbol", league_name, broadcast_key)
                if evt:
                    all_events.append(evt)

    return all_events


def fetch_nba_week():
    """Trae partidos de NBA / playoffs de los próximos 7 días."""
    print("    NBA...")
    all_events = []
    today = datetime.now(MX_TZ)
    seen = set()

    for day_offset in range(8):
        date = today + timedelta(days=day_offset)
        data = _get(f"{BASE}/basketball/nba/scoreboard",
                    params={"dates": date.strftime("%Y%m%d")})
        for event in data.get("events", []):
            eid = event.get("id")
            if eid in seen:
                continue
            seen.add(eid)

            date_str = event.get("date", "")
            event_date, time_mx, _ = _utc_to_mx(date_str)
            if event_date is None:
                continue

            comps = event.get("competitions", [{}])[0]
            competitors = comps.get("competitors", [])
            names = [c.get("team", {}).get("displayName", "") for c in competitors]
            notes = comps.get("notes", [])
            note_text = notes[0].get("headline", "") if notes else ""

            all_events.append({
                "sport": "NBA",
                "league": f"NBA{' — ' + note_text if note_text else ''}",
                "home": names[0] if names else "",
                "away": names[1] if len(names) > 1 else "",
                "date": event_date,
                "time_mx": time_mx,
                "broadcast": _parse_broadcast(comps, "NBA"),
                "favorite": False,
                "home_badge": competitors[0].get("team", {}).get("logo", "") if competitors else "",
                "away_badge": competitors[1].get("team", {}).get("logo", "") if len(competitors) > 1 else "",
            })

    return all_events


def fetch_week():
    """Entry point principal — trae todo."""
    events = []
    events.extend(fetch_football_week())
    events.extend(fetch_nba_week())
    return sorted(events, key=lambda x: (x["date"], x.get("time_mx", "")))

"""
Fetcher principal — ESPN API pública (sin key).
Cubre: fútbol ARG/EUR, Mundial, NBA, Rugby.
"""
import requests
from datetime import datetime, timedelta
import pytz
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FAVORITE_FOOTBALL_TEAMS, MEXICO_BROADCAST, TIMEZONE

BASE = "https://site.api.espn.com/apis/site/v2/sports"
MX_TZ = pytz.timezone(TIMEZONE)

FOOTBALL_SLUGS = [
    ("FIFA.WORLD",                "FIFA World Cup 2026",         "World Cup"),
    ("arg.1",                     "Argentine Primera División",   "Argentine Primera"),
    ("conmebol.libertadores",     "Copa Libertadores",            "Copa Libertadores"),
    ("conmebol.sudamericana",     "Copa Sudamericana",            "Copa Sudamericana"),
    ("UEFA.CHAMPIONS_LEAGUE",     "UEFA Champions League",        "Champions League"),
    ("eng.1",                     "Premier League",               "Premier League"),
    ("esp.1",                     "LaLiga",                       "LaLiga"),
    ("esp.copa_del_rey",          "Copa del Rey",                 "Copa del Rey"),
]


def _get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 400:
            return {}   # liga fuera de temporada — silencioso
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if "400" not in str(e):
            print(f"    [ESPN] Error {url.split('/')[-2]}: {e}")
        return {}


def _utc_to_mx(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        dt_mx = dt.astimezone(MX_TZ)
        return dt_mx.date(), dt_mx.strftime("%H:%M")
    except Exception:
        return None, "TBD"


def _is_favorite(competitors):
    for c in competitors:
        name = c.get("team", {}).get("displayName", "")
        if any(fav.lower() in name.lower() for fav in FAVORITE_FOOTBALL_TEAMS):
            return True
    return False


def _broadcast(comps, default_key):
    for b in comps.get("broadcasts", []):
        names = b.get("names", [])
        if names:
            return ", ".join(names[:2])
    return MEXICO_BROADCAST.get(default_key, "ESPN")


def _parse_event(raw, sport, league_name, broadcast_key):
    date_str = raw.get("date", "")
    event_date, time_mx = _utc_to_mx(date_str)
    if event_date is None:
        return None

    today = datetime.now(MX_TZ).date()
    if not (today <= event_date <= today + timedelta(days=7)):
        return None

    comps = raw.get("competitions", [{}])[0]
    competitors = comps.get("competitors", [])
    names = [
        c.get("team", {}).get("displayName", c.get("athlete", {}).get("displayName", ""))
        for c in competitors
    ]

    # Nota de fase (ej: "Round of 16", "NBA Finals - Game 1")
    notes = comps.get("notes", [])
    note  = notes[0].get("headline", "") if notes else ""

    return {
        "sport":      sport,
        "league":     league_name,
        "home":       names[0] if names else raw.get("name", ""),
        "away":       names[1] if len(names) > 1 else "",
        "date":       event_date,
        "time_mx":    time_mx,
        "broadcast":  _broadcast(comps, broadcast_key),
        "favorite":   _is_favorite(competitors),
        "note":       note,
        "home_badge": competitors[0].get("team", {}).get("logo", "") if competitors else "",
        "away_badge": competitors[1].get("team", {}).get("logo", "") if len(competitors) > 1 else "",
    }


def _fetch_slug(sport_path, slug, league_name, broadcast_key, sport_label="Fútbol"):
    events = []
    today = datetime.now(MX_TZ)
    seen = set()
    for d in range(8):
        date = (today + timedelta(days=d)).strftime("%Y%m%d")
        data = _get(f"{BASE}/{sport_path}/{slug}/scoreboard", params={"dates": date})
        for raw in data.get("events", []):
            eid = raw.get("id")
            if eid in seen:
                continue
            seen.add(eid)
            evt = _parse_event(raw, sport_label, league_name, broadcast_key)
            if evt:
                events.append(evt)
    return events


def fetch_football_week():
    all_events = []
    for slug, league_name, bcast_key in FOOTBALL_SLUGS:
        print(f"    {league_name}...")
        all_events.extend(_fetch_slug("soccer", slug, league_name, bcast_key, "Fútbol"))
    return all_events


def fetch_nba_week():
    print("    NBA...")
    events = []
    today = datetime.now(MX_TZ)
    seen = set()
    for d in range(8):
        date = (today + timedelta(days=d)).strftime("%Y%m%d")
        data = _get(f"{BASE}/basketball/nba/scoreboard", params={"dates": date})
        for raw in data.get("events", []):
            eid = raw.get("id")
            if eid in seen:
                continue
            seen.add(eid)
            event_date, time_mx = _utc_to_mx(raw.get("date",""))
            if event_date is None:
                continue
            comps = raw.get("competitions", [{}])[0]
            competitors = comps.get("competitors", [])
            names = [c.get("team", {}).get("displayName", "") for c in competitors]
            notes = comps.get("notes", [])
            note  = notes[0].get("headline", "") if notes else ""
            events.append({
                "sport":      "NBA",
                "league":     f"NBA — {note}" if note else "NBA",
                "home":       names[0] if names else "",
                "away":       names[1] if len(names) > 1 else "",
                "date":       event_date,
                "time_mx":    time_mx,
                "broadcast":  _broadcast(comps, "NBA"),
                "favorite":   False,
                "note":       note,
                "home_badge": competitors[0].get("team",{}).get("logo","") if competitors else "",
                "away_badge": competitors[1].get("team",{}).get("logo","") if len(competitors)>1 else "",
            })
    return events


def fetch_week():
    events = []
    events.extend(fetch_football_week())
    events.extend(fetch_nba_week())
    return events

import requests
from datetime import datetime, timedelta
import pytz
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import TIMEZONE, MEXICO_BROADCAST

BASE_URL = "https://api.jolpi.ca/ergast/f1"
MX_TZ = pytz.timezone(TIMEZONE)


def _get(endpoint):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [F1 API] Error en {endpoint}: {e}")
        return {}


def _parse_session(date_str, time_str, label, circuit, round_name, season):
    """Convierte una sesión de F1 a evento normalizado."""
    if not date_str:
        return None
    try:
        dt_str = f"{date_str}T{time_str}" if time_str else f"{date_str}T12:00:00Z"
        dt_utc = datetime.strptime(dt_str.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
        dt_mx = dt_utc.astimezone(MX_TZ)
        today = datetime.now(MX_TZ).date()
        if dt_mx.date() < today:
            return None
        if dt_mx.date() > today + timedelta(days=7):
            return None
        return {
            "sport": "Fórmula 1",
            "league": f"F1 {season}",
            "home": f"{label} — {round_name}",
            "away": circuit,
            "date": dt_mx.date(),
            "time_mx": dt_mx.strftime("%H:%M"),
            "broadcast": MEXICO_BROADCAST.get("F1", "F1 TV / ESPN"),
            "favorite": True,  # F1 siempre destacado para el grupo
            "home_badge": "",
            "away_badge": "",
        }
    except Exception as e:
        print(f"  [F1] parse error: {e}")
        return None


def fetch_week_events():
    print("  Consultando F1...")
    data = _get("/current/next.json")
    try:
        race = data["MRData"]["RaceTable"]["Races"][0]
    except (KeyError, IndexError):
        return []

    season = race.get("season", "")
    round_name = race.get("raceName", "")
    circuit = race.get("Circuit", {}).get("circuitName", "")

    sessions = [
        ("Práctica 1",  race.get("FirstPractice", {}).get("date"),  race.get("FirstPractice", {}).get("time")),
        ("Práctica 2",  race.get("SecondPractice", {}).get("date"), race.get("SecondPractice", {}).get("time")),
        ("Práctica 3",  race.get("ThirdPractice", {}).get("date"),  race.get("ThirdPractice", {}).get("time")),
        ("Sprint",      race.get("Sprint", {}).get("date"),         race.get("Sprint", {}).get("time")),
        ("Clasificación", race.get("Qualifying", {}).get("date"),   race.get("Qualifying", {}).get("time")),
        ("CARRERA",     race.get("date"),                           race.get("time")),
    ]

    events = []
    for label, date_str, time_str in sessions:
        if not date_str:
            continue
        evt = _parse_session(date_str, time_str, label, circuit, round_name, season)
        if evt:
            events.append(evt)

    return events

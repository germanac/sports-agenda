"""
Sistema de scoring de relevancia para el grupo Koleos.
Retorna un score (menor = más prioritario) y tags de display.
"""
from config import (
    FAVORITE_FOOTBALL_TEAMS, TOP_NATIONAL_TEAMS,
    MINOR_NATIONS, RUGBY_PRIORITY_TEAMS, RUGBY_MAJOR_COMPETITIONS
)


def _contains(text, terms):
    t = text.lower()
    return any(term.lower() in t for term in terms)


def score_football(event):
    """
    Retorna (score, is_favorite, tags).
    Score: 0 = imperdible, 100 = ignorar.
    """
    home   = event.get("home", "")
    away   = event.get("away", "")
    league = event.get("league", "")
    both   = f"{home} {away} {league}"

    tags = []
    score = 50  # default

    # ── Favoritos del grupo ──────────────────────────────────────
    is_fav = _contains(both, FAVORITE_FOOTBALL_TEAMS)
    if is_fav:
        score = 0
        if _contains(both, ["River Plate"]):
            tags.append("🔴⚪ RIVER")
        if _contains(both, ["Boca Juniors"]):
            tags.append("🔵🟡 BOCA")
        if _contains(both, ["Estudiantes"]):
            tags.append("🔴⚫ EL PINCHA")

    # ── Mundial (lógica especial) ────────────────────────────────
    if "world" in league.lower() or "mundial" in league.lower() or "FIFA.WORLD" in league:
        phase = event.get("phase", "").lower()
        note  = event.get("note", "").lower()
        is_knockout = any(x in note for x in ["round of 16", "quarter", "semi", "final",
                                               "octavos", "cuartos", "semis"])
        has_top = _contains(both, TOP_NATIONAL_TEAMS)
        has_arg = _contains(both, ["Argentina"])

        if has_arg:
            score = 0; tags.append("🇦🇷 ARGENTINA"); is_fav = True
        elif is_knockout:
            score = 5; tags.append("🏆 MUNDIAL KO")
        elif has_top:
            score = 10; tags.append("🌍 MUNDIAL")
        else:
            # Fase de grupos, sin selecciones top → ignorar
            return 90, False, []

    # ── Ligas europeas ───────────────────────────────────────────
    elif _contains(league, ["Champions", "UEFA Champions"]):
        phase = event.get("note", "").lower()
        if any(x in phase for x in ["final", "semi", "quarter", "cuarto"]):
            score = min(score, 5); tags.append("👑 UCL")
        elif not is_fav:
            score = min(score, 20); tags.append("🏆 UCL")

    elif _contains(league, ["Premier League", "Premier"]):
        score = min(score, 25); tags.append("🏴󠁧󠁢󠁥󠁮󠁧󠁿 PREMIER")

    elif _contains(league, ["LaLiga", "Liga Española", "esp.1", "española"]):
        score = min(score, 30); tags.append("🇪🇸 LALIGA")

    elif _contains(league, ["Copa del Rey"]):
        score = min(score, 35); tags.append("🥇 COPA REY")

    elif _contains(league, ["Argentine Primera", "arg.1", "Primera División"]):
        if not is_fav:
            score = min(score, 15); tags.append("🇦🇷 ARG")

    elif _contains(league, ["Libertadores"]):
        score = min(score, 20); tags.append("🏆 LIBERTADORES")

    elif _contains(league, ["Sudamericana"]):
        score = min(score, 25); tags.append("🏆 SUDAMERICANA")

    return score, is_fav, tags


def score_rugby(event):
    home   = event.get("home", "")
    away   = event.get("away", "")
    league = event.get("league", "")
    both   = f"{home} {away} {league}"

    has_arg = _contains(both, RUGBY_PRIORITY_TEAMS)
    is_major = _contains(league, RUGBY_MAJOR_COMPETITIONS)
    is_sevens = "seven" in league.lower()

    if has_arg:
        score = 5 if not is_sevens else 10
        tags  = ["🇦🇷 PUMAS"]
        is_fav = True
    elif is_major:
        # Solo partidos entre selecciones importantes
        minor_involved = _contains(both, list(MINOR_NATIONS))
        score = 20 if not minor_involved else 60
        tags  = ["🏉 RUGBY INT"]
        is_fav = False
    else:
        score = 70
        tags  = []
        is_fav = False

    return score, is_fav, tags


def score_f1(event):
    home = event.get("home", "").upper()
    if "CARRERA" in home:
        return 3, True, ["🏁 CARRERA"]
    if "CLASIFICACIÓN" in home or "QUALIFYING" in home:
        return 8, True, ["⏱ QUALY"]
    if "SPRINT" in home:
        return 12, True, ["⚡ SPRINT"]
    return 40, False, ["🏎 F1"]


def score_nba(event):
    league = event.get("league", "")
    if "Finals" in league and "Game" in league:
        return 8, True, ["🏆 NBA FINALS"]
    if "Finals" in league:
        return 10, True, ["🏆 NBA FINALS"]
    if any(x in league for x in ["Semifinal", "Conference", "Playoff"]):
        return 15, False, ["🏀 PLAYOFFS"]
    return 80, False, []   # regular season → ignorar


def score_tennis(event):
    league = event.get("league", "")
    home   = event.get("home", "")
    is_slam = any(x in league for x in
                  ["Roland Garros", "Wimbledon", "US Open", "Australian Open", "Grand Slam"])
    has_arg = _contains(f"{home} {league}", ["Argentina", "Etcheverry", "Cerundolo", "Navone", "Báez"])
    phase_late = any(x in home.lower() for x in ["final", "semifinal", "quarter"])

    if has_arg:
        return 10, True, ["🇦🇷 ARG TENIS"]
    if is_slam and phase_late:
        return 15, False, ["🎾 SLAM FINAL"]
    if is_slam:
        return 30, False, ["🎾 SLAM"]
    return 70, False, []


def score_event(event):
    """
    Puntúa un evento. Retorna el evento enriquecido con score, is_fav, tags.
    Si score >= 90 → descartar.
    """
    sport = event.get("sport", "")
    if sport == "Fútbol":
        s, fav, tags = score_football(event)
    elif sport == "Rugby":
        s, fav, tags = score_rugby(event)
    elif sport == "Fórmula 1":
        s, fav, tags = score_f1(event)
    elif sport == "NBA":
        s, fav, tags = score_nba(event)
    elif sport == "Tenis":
        s, fav, tags = score_tennis(event)
    else:
        s, fav, tags = 50, False, []

    return {**event, "score": s, "favorite": fav, "display_tags": tags}


def filter_and_sort(events):
    """Filtra eventos irrelevantes y ordena por (score, fecha, hora)."""
    scored = [score_event(e) for e in events]
    filtered = [e for e in scored if e["score"] < 90]
    return sorted(filtered, key=lambda e: (e["score"], e["date"], e.get("time_mx", "")))

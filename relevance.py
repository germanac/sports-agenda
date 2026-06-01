"""
Sistema de relevancia para el grupo Koleos.
El score refleja el valor deportivo real del evento, no una lista de nombres.
Score: 0 = imperdible, 100 = ignorar.
"""
from config import FAVORITE_FOOTBALL_TEAMS, TIMEZONE
import pytz

MX_TZ = pytz.timezone(TIMEZONE)

# ── Tier de selecciones de fútbol (por ranking FIFA / historial competitivo) ──
#
# Tier 1 — candidatos al título, siempre relevantes
TIER1_NATIONS = {
    "france", "brazil", "argentina", "england", "spain", "germany",
    "portugal", "netherlands", "belgium", "croatia", "italy", "uruguay",
}
# Tier 2 — selecciones sólidas, interesantes en contexto
TIER2_NATIONS = {
    "denmark", "switzerland", "austria", "turkey", "poland", "serbia",
    "colombia", "mexico", "usa", "united states", "senegal", "morocco",
    "japan", "south korea", "ecuador", "chile", "peru", "nigeria",
    "côte d'ivoire", "ivory coast", "egypt", "australia", "new zealand",
    "wales", "scotland", "czech republic", "czechia", "hungary", "ukraine",
    "slovakia", "iran", "saudi arabia", "south africa",
}
# Tier 3 — el resto: no interesan en fase de grupos del Mundial

# ── Tier de clubes de fútbol ──────────────────────────────────────────────────
# Clubes que siempre son relevantes en Champions/Premier/LaLiga
ELITE_CLUBS = {
    # España
    "real madrid", "barcelona", "atletico madrid", "athletic bilbao", "villarreal",
    # Inglaterra
    "manchester city", "arsenal", "liverpool", "chelsea", "manchester united",
    "tottenham", "newcastle", "aston villa",
    # Alemania (si vuelve a Champions)
    "bayern munich", "borussia dortmund", "bayer leverkusen",
    # Italia
    "inter", "milan", "juventus", "napoli",
    # Francia
    "paris saint-germain", "psg",
    # Argentina — ya cubiertos por FAVORITE_FOOTBALL_TEAMS
    "river plate", "boca juniors", "estudiantes",
    "racing", "independiente", "san lorenzo", "velez",
    # Brasil (Libertadores)
    "flamengo", "palmeiras", "fluminense", "atletico mineiro",
}

# ── Palabras clave de fase eliminatoria ────────────────────────────────────────
KNOCKOUT_KEYWORDS = {
    "final", "semifinal", "semi-final", "quarter", "cuarto",
    "round of 16", "octavos", "last 16", "r16",
    "copa", "championship", "title",
}

PHASE_WEIGHT = {
    "final":       0,
    "semifinal":   3,
    "quarterfinal":7,
    "round of 16": 12,
}


def _t(text):
    return str(text).lower().strip()


def _in(text, group):
    t = _t(text)
    return any(item in t for item in group)


def _tier(nation_name):
    n = _t(nation_name)
    if n in TIER1_NATIONS:
        return 1
    if n in TIER2_NATIONS:
        return 2
    return 3


def _is_club_elite(name):
    return _in(name, ELITE_CLUBS)


def _is_club_favorite(name):
    favs = [_t(f) for f in FAVORITE_FOOTBALL_TEAMS]
    return _in(name, favs)


def _knockout_phase(note):
    """Detecta si el partido es eliminatorio y qué fase, desde la nota del evento."""
    n = _t(note)
    for kw, weight in PHASE_WEIGHT.items():
        if kw in n:
            return True, weight
    for kw in KNOCKOUT_KEYWORDS:
        if kw in n:
            return True, 10
    return False, 99


def _match_value(home, away, note=""):
    """
    Calcula el valor de un partido entre home y away.
    Retorna score base (sin aplicar peso de liga).
    """
    # Favoritos del grupo → siempre
    if _is_club_favorite(home) or _is_club_favorite(away):
        return 0, True

    # Elite clubs → alta prioridad
    home_elite = _is_club_elite(home)
    away_elite = _is_club_elite(away)

    is_ko, phase_score = _knockout_phase(note)

    if home_elite and away_elite:
        return min(5, phase_score), False    # partido grande
    if home_elite or away_elite:
        return min(20, phase_score + 10), False
    if is_ko:
        return phase_score + 5, False       # knockout sin élite = algo importa
    return 50, False                         # partido genérico


def _national_match_value(home, away, note="", league=""):
    """Valor de un partido entre selecciones."""
    h_tier = _tier(home)
    a_tier = _tier(away)

    # Argentina → siempre
    if _in(home, ["argentina"]) or _in(away, ["argentina"]):
        return 0, True

    is_ko, phase_score = _knockout_phase(note)
    league_l = _t(league)

    # Final de cualquier cosa → mostrar
    if "final" in league_l or phase_score == 0:
        return 2, False

    # Ambos Tier 1 → siempre interesante
    if h_tier == 1 and a_tier == 1:
        return 8, False

    # Un Tier1 vs Tier2 → depende de la fase
    if min(h_tier, a_tier) == 1:
        if is_ko:
            return 10, False
        return 18, False    # grupo con top

    # Tier2 vs Tier2 → solo si es fase eliminatoria o competencia importante
    if h_tier == 2 and a_tier == 2:
        if is_ko:
            return 20, False
        return 55, False    # poco interesante en grupos

    # Tier3 involucrado → ignorar salvo que sea KO de competencia mayor
    if is_ko and phase_score <= 12:
        return 40, False
    return 90, False         # descartar


def score_football(event):
    home   = event.get("home", "")
    away   = event.get("away", "")
    league = event.get("league", "")
    note   = event.get("note", "")
    tags   = []

    is_national = _in(league, [
        "world cup", "mundial", "copa america", "euro", "nations league",
        "conmebol qualif", "world qualif", "six nations", "nations cup",
    ])

    if is_national:
        score, is_fav = _national_match_value(home, away, note, league)
        if _in(home + away, ["argentina"]):
            tags.append("🇦🇷 ARGENTINA")
        elif score <= 8:
            tags.append("🌍 MUNDIAL TOP")
        elif score <= 20:
            tags.append("🌍 MUNDIAL")
        elif score < 88:
            tags.append("🌍 GRUPO")
    else:
        score, is_fav = _match_value(home, away, note)

        # Tags por liga
        if _in(league, ["world cup", "fifa.world"]):
            tags.append("🏆 MUNDIAL")
        elif _in(league, ["champions"]):
            is_ko, ps = _knockout_phase(note)
            tags.append("👑 UCL FINAL" if ps <= 3 else "👑 UCL")
        elif _in(league, ["premier"]):
            tags.append("🏴󠁧󠁢󠁥󠁮󠁧󠁿 PREMIER")
        elif _in(league, ["laliga", "esp.1", "española"]):
            tags.append("🇪🇸 LALIGA")
        elif _in(league, ["copa del rey"]):
            tags.append("🥇 COPA REY")
        elif _in(league, ["argentine", "arg.1", "primera"]):
            tags.append("🇦🇷 ARG")
        elif _in(league, ["libertadores"]):
            tags.append("🏆 LIBERTADORES")
        elif _in(league, ["sudamericana"]):
            tags.append("🏆 SUDAMERICANA")

        # Tags por equipo favorito
        if _is_club_favorite(home) or _is_club_favorite(away):
            for fav in FAVORITE_FOOTBALL_TEAMS:
                if _in(home + away, [_t(fav)]):
                    emojis = {"river plate":"🔴⚪","boca juniors":"🔵🟡","estudiantes":"🔴⚫"}
                    tags.insert(0, f"{emojis.get(_t(fav),'⚽')} {fav.split()[0].upper()}")

    return score, is_fav, tags


def score_rugby(event):
    home   = event.get("home", "")
    away   = event.get("away", "")
    league = event.get("league", "")
    note   = event.get("note", "")

    has_arg   = _in((home or "") + (away or ""), ["argentina", "pumas"])
    is_sevens = "seven" in _t(league)
    is_ko, ps = _knockout_phase(note)

    # Selecciones de primera línea en rugby
    rugby_top = {"new zealand", "south africa", "ireland", "france", "england",
                 "australia", "scotland", "wales", "argentina"}
    h_top = _in(home, rugby_top)
    a_top = _in(away, rugby_top)

    if has_arg:
        return 5, True, ["🇦🇷 PUMAS"]
    if _in(league, ["world cup"]):
        if h_top and a_top:
            return 6, False, ["🏆 RWC"]
        if is_ko:
            return 12, False, ["🏆 RWC KO"]
        if h_top or a_top:
            return 20, False, ["🏉 RWC"]
        return 85, False, []
    if _in(league, ["six nations", "rugby championship", "championship"]):
        if h_top and a_top:
            return 15, False, ["🏉 INT"]
        if is_ko or "final" in _t(note):
            return 12, False, ["🏉 FINAL"]
        return 35, False, ["🏉 INT"]

    return 70, False, []


def score_f1(event):
    home = _t(event.get("home", ""))
    if "carrera" in home or "race" in home:
        return 3, True, ["🏁 CARRERA"]
    if "clasificación" in home or "qualifying" in home:
        return 8, True, ["⏱ QUALY"]
    if "sprint" in home:
        return 12, True, ["⚡ SPRINT"]
    # Prácticas: solo mostrar si no hay eventos más importantes
    return 45, False, ["🏎 PRÁCTICA"]


def score_nba(event):
    league = event.get("league", "")
    note   = event.get("note", "")
    l = _t(league + note)

    if "finals" in l and ("game" in l or "final" in l):
        return 8, True, ["🏆 NBA FINALS"]
    if "conference final" in l or "conference semi" in l:
        return 15, False, ["🏀 PLAYOFFS"]
    if "playoff" in l or "postseason" in l:
        return 30, False, ["🏀 PLAYOFFS"]
    return 85, False, []   # regular season → ignorar


def score_tennis(event):
    league = event.get("league", "")
    home   = event.get("home", "")
    l = _t(league + home)

    # Argentinos en el circuito
    arg_players = ["etcheverry", "cerundolo", "navone", "báez", "baez", "argentina"]
    has_arg = any(p in l for p in arg_players)

    is_slam = any(x in l for x in ["roland garros","wimbledon","us open","australian open","grand slam"])
    # Etapa definitoria = SF o F
    is_late = any(x in l for x in ["semifinal","final","sf","qf","quarter"])

    if has_arg:
        return 10, True, ["🇦🇷 ARG TENIS"]
    if is_slam and is_late:
        return 12, False, ["🎾 SLAM FINAL"]
    if is_slam:
        return 28, False, ["🎾 SLAM"]
    return 75, False, []


# ── Entry point ────────────────────────────────────────────────────────────────

def score_event(event):
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
    scored   = [score_event(e) for e in events]
    filtered = [e for e in scored if e["score"] < 88]
    return sorted(filtered, key=lambda e: (e["score"], e["date"], e.get("time_mx", "")))

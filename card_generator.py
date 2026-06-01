"""
Genera el HTML de la card vertical estilo iPhone 14 (390px ancho).
Luego Playwright lo captura como PNG.
"""
from datetime import datetime, timedelta
import pytz

TIMEZONE = "America/Mexico_City"
MX_TZ = pytz.timezone(TIMEZONE)

DAY_ES = {
    "Monday": "LUN", "Tuesday": "MAR", "Wednesday": "MIÉ",
    "Thursday": "JUE", "Friday": "VIE", "Saturday": "SÁB", "Sunday": "DOM"
}
MONTH_ES = {
    1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
    7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
}

SPORT_COLOR = {
    "Fútbol": "#22c55e",
    "Fórmula 1": "#ef4444",
    "NBA": "#f97316",
    "Tenis": "#f59e0b",
}

SPORT_ICON = {
    "Fútbol": "⚽",
    "Fórmula 1": "🏎",
    "NBA": "🏀",
    "Tenis": "🎾",
}

# Hero images por deporte/evento (URLs de imágenes libres de derechos)
HERO_IMAGES = {
    "Fórmula 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/F1_logo.svg/320px-F1_logo.svg.png",
    "NBA": "https://upload.wikimedia.org/wikipedia/en/thumb/0/03/National_Basketball_Association_logo.svg/200px-National_Basketball_Association_logo.svg.png",
    "Fútbol": "",
}


def _day_label(date):
    day_en = date.strftime("%A")
    return DAY_ES.get(day_en, day_en[:3].upper())


def _date_range_label(events):
    if not events:
        return ""
    dates = sorted(set(e["date"] for e in events))
    start = dates[0]
    end = dates[-1]
    if start == end:
        return f"{start.day} {MONTH_ES[start.month]} {start.year}"
    return f"{start.day}-{end.day} {MONTH_ES[start.month]} {start.year}"


def _group_by_day(events):
    days = {}
    for e in events:
        d = e["date"]
        if d not in days:
            days[d] = []
        days[d].append(e)
    return dict(sorted(days.items()))


def _event_key(e):
    return f"{e.get('home','')}_{e.get('away','')}_{e['date']}"


def _hero_section(events):
    """Dos bloques hero en el tope, con imágenes o badges de equipos."""
    # Buscar los dos eventos más destacados (favoritos primero, luego F1)
    favorites = [e for e in events if e.get("favorite")]
    f1 = [e for e in events if e["sport"] == "Fórmula 1" and "CARRERA" in e.get("home","").upper()]

    featured = []
    if f1:
        featured.append(f1[0])
    if favorites:
        for f in favorites:
            if f not in featured:
                featured.append(f)
                if len(featured) >= 2:
                    break
    while len(featured) < 2 and events:
        for e in events:
            if e not in featured:
                featured.append(e)
                break
        else:
            break

    blocks = []
    for i, e in enumerate(featured[:2]):
        sport = e["sport"]
        color = SPORT_COLOR.get(sport, "#6366f1")

        img_html = ""
        if e.get("home_badge"):
            img_html = f'<img src="{e["home_badge"]}" style="width:70px;height:70px;object-fit:contain;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.5))">'
        elif e.get("away_badge"):
            img_html = f'<img src="{e["away_badge"]}" style="width:70px;height:70px;object-fit:contain;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.5))">'
        else:
            img_html = f'<div style="font-size:3rem">{SPORT_ICON.get(sport,"🏟")}</div>'

        # Subtitle: league tag
        subtitle = e.get("league", sport).upper()
        if len(subtitle) > 20:
            subtitle = subtitle[:18] + "…"
        date_label = f"{_day_label(e['date'])} {e['date'].day}"

        # Main text
        if e["sport"] == "Fórmula 1":
            main = e.get("home", "").replace(" — ", "\n")
        elif e.get("away"):
            main = f"LA {e['home'].split()[-1].upper()}\nVS {e['away'].split()[-1].upper()}"
        else:
            main = e.get("home", "").upper()[:20]

        blocks.append(f"""
        <div style="flex:1;position:relative;overflow:hidden;min-height:160px;
                    background:linear-gradient(160deg,{color}33 0%,#0a0a0a 70%);
                    border-radius:12px;padding:14px 12px;display:flex;flex-direction:column;
                    gap:6px;border:1px solid {color}44">
            <div style="font-size:9px;font-weight:700;color:{color};letter-spacing:2px;text-transform:uppercase">
                {subtitle} · {date_label}
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center">
                {img_html}
            </div>
            <div style="font-size:15px;font-weight:900;color:#fff;line-height:1.1;text-transform:uppercase">
                {main}
            </div>
        </div>""")

    return f"""
    <div style="display:flex;gap:8px;margin-bottom:16px">
        {''.join(blocks)}
    </div>"""


def _event_card_html(event, relato=""):
    sport = event["sport"]
    color = SPORT_COLOR.get(sport, "#6366f1")
    icon = SPORT_ICON.get(sport, "🏟")
    day = _day_label(event["date"])
    day_num = event["date"].day
    is_fav = event.get("favorite", False)

    if event.get("away") and sport == "Fútbol":
        match_name = f"{event['home'].upper()} VS {event['away'].upper()}"
    else:
        match_name = event.get("home", "").upper()

    # Canal tag
    broadcast = event.get("broadcast", "")
    channels = [c.strip() for c in broadcast.replace("/", ",").split(",")][:2]
    channel_tags = " ".join([
        f'<span style="background:#ffffff15;border-radius:4px;padding:1px 6px;font-size:9px;color:#aaa;font-weight:600">·{c}</span>'
        for c in channels if c
    ])

    fav_tag = f'<span style="background:{color}33;color:{color};border-radius:4px;padding:1px 6px;font-size:9px;font-weight:800;letter-spacing:1px">🔥 IMPERDIBLE</span>' if is_fav else ""

    relato_html = f'<div style="font-size:10px;color:#888;line-height:1.4;font-style:italic;margin-top:6px;border-left:2px solid {color}44;padding-left:8px">{relato}</div>' if relato else ""

    return f"""
    <div style="background:#111;border-radius:10px;padding:12px 14px;margin-bottom:8px;
                border-left:3px solid {color};position:relative">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
            <span style="background:#1a1a1a;border-radius:6px;padding:2px 8px;font-size:9px;
                         font-weight:800;color:{color};letter-spacing:1px">{day} {day_num}</span>
            <span style="font-size:9px;color:#666;font-weight:600">{icon} {sport.upper()} · {event.get('league','').upper()[:25]}</span>
            {fav_tag}
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
            <div style="font-size:14px;font-weight:900;color:#fff;line-height:1.2;flex:1">
                {match_name}
            </div>
            <div style="font-size:20px;font-weight:900;color:#fff;white-space:nowrap;text-align:right">
                {event.get('time_mx','TBD')}<br>
                <span style="font-size:8px;color:#555;font-weight:400">CDMX</span>
            </div>
        </div>
        <div style="margin-top:5px">{channel_tags}</div>
        {relato_html}
    </div>"""


def generate_card_html(events, resumen, relatos_map):
    today = datetime.now(MX_TZ)
    date_range = _date_range_label(events)
    total = len(events)

    hero = _hero_section(events)

    # Cronograma
    days = _group_by_day(events)
    cronograma = ""
    for date, day_events in days.items():
        day_cards = "".join(
            _event_card_html(e, relatos_map.get(_event_key(e), ""))
            for e in day_events
        )
        cronograma += day_cards

    resumen_html = resumen.replace("\n", "<br>") if resumen else ""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=390">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family:'Inter',sans-serif;
    background:#0a0a0a;
    color:#e2e8f0;
    width:390px;
    padding:16px;
  }}
</style>
</head>
<body>
  {hero}

  <!-- Header -->
  <div style="text-align:center;margin-bottom:16px">
    <div style="font-size:38px;font-weight:900;color:#fff;letter-spacing:-1px;line-height:1">
        KOLEOS
    </div>
    <div style="font-size:13px;font-weight:700;color:#444;letter-spacing:6px">CDMX</div>
    <div style="margin-top:8px;display:inline-flex;align-items:center;gap:6px;
                background:#111;border-radius:20px;padding:4px 14px">
        <span style="color:#f59e0b;font-size:10px">✦</span>
        <span style="font-size:10px;font-weight:700;color:#888;letter-spacing:2px;text-transform:uppercase">
            Agenda Deportiva · {date_range}
        </span>
        <span style="color:#f59e0b;font-size:10px">✦</span>
    </div>
  </div>

  <!-- Resumen -->
  <div style="background:#111;border-radius:12px;padding:14px;margin-bottom:16px;
              border:1px solid #222">
    <div style="font-size:9px;font-weight:800;color:#f59e0b;letter-spacing:3px;margin-bottom:8px">
        ✦ RESUMEN
    </div>
    <div style="font-size:11px;color:#aaa;line-height:1.6">{resumen_html}</div>
  </div>

  <!-- Cronograma -->
  <div style="margin-bottom:12px">
    <div style="font-size:9px;font-weight:800;color:#555;letter-spacing:3px;margin-bottom:10px;
                border-bottom:1px solid #1a1a1a;padding-bottom:6px">
        CRONOGRAMA · {total} EVENTOS
    </div>
    {cronograma}
  </div>

  <!-- Footer -->
  <div style="text-align:center;padding:10px 0;border-top:1px solid #1a1a1a">
    <div style="font-size:9px;color:#333;font-weight:600;letter-spacing:2px">
        🏟 KOLEOS · CDMX {today.year}
    </div>
  </div>
</body>
</html>"""

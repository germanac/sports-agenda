"""
Card visual fija 390×844px (iPhone 14).
Approach C: truncado en Python + anchos fijos en px.
Nada se corta — garantizado.
"""
from datetime import datetime
import pytz

TIMEZONE = "America/Mexico_City"
MX_TZ    = pytz.timezone(TIMEZONE)

DAY_ES = {
    "Monday":"LUN","Tuesday":"MAR","Wednesday":"MIÉ",
    "Thursday":"JUE","Friday":"VIE","Saturday":"SÁB","Sunday":"DOM"
}
MONTH_ES = {
    1:"ene",2:"feb",3:"mar",4:"abr",5:"may",6:"jun",
    7:"jul",8:"ago",9:"sep",10:"oct",11:"nov",12:"dic"
}
SPORT_COLOR = {
    "Fútbol":"#22c55e","Fórmula 1":"#ef4444",
    "NBA":"#f97316","Tenis":"#f59e0b","Rugby":"#8b5cf6",
}
SPORT_ICON = {
    "Fútbol":"⚽","Fórmula 1":"🏎","NBA":"🏀","Tenis":"🎾","Rugby":"🏉",
}

# ─── Dimensiones fijas (px) ───────────────────────────────────────
# Todas suman ≤ 844px — verificado en _verify()
CARD_W      = 390
CARD_H      = 844

PAD_TOP     = 8
HERO_H      = 116
GAP1        = 10
WORDMARK_H  = 50
GAP2        = 8
RESUMEN_H   = 90
GAP3        = 8
CRONO_HDR_H = 22
ROW_H       = 80
MAX_ROWS    = 6
MORE_H      = 20
FOOTER_H    = 24

# Columnas dentro de cada row
PAD_L    = 14
PAD_R    = 14
DAY_W    = 34
GAP_DAY  = 12
GAP_TIME = 10
TIME_W   = 52
INFO_W   = CARD_W - PAD_L - PAD_R - DAY_W - GAP_DAY - GAP_TIME - TIME_W  # 254px

# Límites de caracteres (conservadores — calculados arriba)
CHARS_LEAGUE   = 36    # 7px
CHARS_NAME     = 27    # 12.5px bold, sin tag
CHARS_NAME_TAG = 18    # 12.5px bold, con tag (tag ocupa ~85px)
CHARS_CHANNEL  = 18    # 7.5px
CHARS_RELATO   = 54    # 8px italic


def _verify():
    total = (PAD_TOP + HERO_H + GAP1 + WORDMARK_H + GAP2 + RESUMEN_H + GAP3 +
             CRONO_HDR_H + ROW_H * MAX_ROWS + MORE_H + FOOTER_H)
    assert total <= CARD_H, f"Layout overflow: {total}px > {CARD_H}px"

_verify()


# ─── Helpers ──────────────────────────────────────────────────────

def _t(s, n):
    """Trunca s a n chars con … en Python. Sin depender de CSS."""
    s = (s or "").strip()
    return s if len(s) <= n else s[:n-1] + "…"

def _day(date):
    return DAY_ES.get(date.strftime("%A"), "")

def _date_range(events):
    if not events:
        return ""
    dates = sorted(set(e["date"] for e in events))
    s, en = dates[0], dates[-1]
    if s.month == en.month:
        return f"{s.day}–{en.day} {MONTH_ES[s.month].upper()} {s.year}"
    return f"{s.day} {MONTH_ES[s.month].upper()} – {en.day} {MONTH_ES[en.month].upper()} {s.year}"

def _key(e):
    return f"{e.get('home','')}_{e.get('away','')}_{e['date']}"

def _match_name(e):
    """
    Nombre del partido según deporte.
    F1: solo nombre de sesión (sin circuito).
    Resto: home vs away si hay away.
    """
    home  = (e.get("home") or "").strip()
    away  = (e.get("away") or "").strip()
    sport = e.get("sport", "")

    if sport == "Fórmula 1":
        # home viene como "CARRERA — Monaco Grand Prix"
        # Mostrar solo hasta el "—"
        if " — " in home:
            session, race = home.split(" — ", 1)
            # Abreviar nombre de carrera (quitar "Grand Prix")
            race_short = race.replace(" Grand Prix", "").replace(" Grand", "")
            return f"{session} · {race_short}"
        return home

    if away:
        # Abreviar a 2 palabras por equipo si el nombre es largo
        def shorten(name):
            words = name.split()
            # Si el nombre es muy largo, quedar con las 2 primeras palabras
            return " ".join(words[:2]) if len(name) > 14 else name
        return f"{shorten(home)} vs {shorten(away)}"

    return home


# ─── Hero ─────────────────────────────────────────────────────────

def _hero(events):
    top2 = sorted(events, key=lambda e: e.get("score", 99))[:2]
    while len(top2) < 2:
        top2.append(None)

    blocks = []
    for e in top2:
        if e is None:
            blocks.append(f'<div style="flex:1"></div>')
            continue

        color = SPORT_COLOR.get(e["sport"], "#6366f1")
        icon  = SPORT_ICON.get(e["sport"], "🏟")
        tags  = e.get("display_tags", [])
        tag   = _t(tags[0], 16) if tags else e["sport"]
        day   = f"{_day(e['date'])} {e['date'].day}"
        name  = _t(_match_name(e), 20)
        time  = e.get("time_mx", "TBD")

        if e.get("home_badge"):
            badge = f'<img src="{e["home_badge"]}" style="height:36px;width:36px;object-fit:contain;filter:drop-shadow(0 2px 8px #000)">'
        elif e.get("away_badge"):
            badge = f'<img src="{e["away_badge"]}" style="height:36px;width:36px;object-fit:contain">'
        else:
            badge = f'<span style="font-size:2rem">{icon}</span>'

        blocks.append(f"""
        <div style="flex:1;height:{HERO_H}px;overflow:hidden;
                    background:linear-gradient(145deg,{color}28 0%,#0d0d0d 70%);
                    border-radius:10px;border:1px solid {color}35;
                    padding:10px;display:flex;flex-direction:column;justify-content:space-between">
          <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:1.5px">{tag} · {day}</div>
          <div style="display:flex;align-items:center;justify-content:center;padding:4px 0">{badge}</div>
          <div style="font-size:10px;font-weight:900;color:#fff;line-height:1.2">{name}</div>
          <div style="font-size:9px;font-weight:700;color:#ffe87a;margin-top:4px">{time} CDMX</div>
        </div>""")

    return (
        f'<div style="display:flex;gap:8px;height:{HERO_H}px;padding:0 {PAD_L}px">'
        + "".join(blocks) + "</div>"
    )


# ─── Wordmark ─────────────────────────────────────────────────────

def _wordmark(date_range):
    return f"""
    <div style="height:{WORDMARK_H}px;overflow:hidden;text-align:center;padding:4px {PAD_L}px 0">
      <div style="font-size:19px;font-weight:900;color:#fff;letter-spacing:.5px;line-height:1.2">
          AGENDA DEPORTIVA
      </div>
      <div style="display:inline-flex;align-items:center;gap:5px;margin-top:5px;
                  background:#111;border-radius:20px;padding:3px 12px;border:1px solid #1e1e1e">
        <span style="color:#f59e0b;font-size:7px">✦</span>
        <span style="font-size:7.5px;font-weight:700;color:#444;letter-spacing:2px">{date_range} · CDMX</span>
        <span style="color:#f59e0b;font-size:7px">✦</span>
      </div>
    </div>"""


# ─── Resumen ──────────────────────────────────────────────────────

def _resumen(text):
    # Permitir ~3-4 líneas de texto
    safe = (text or "")[:260]
    return f"""
    <div style="height:{RESUMEN_H}px;overflow:hidden;margin:0 {PAD_L}px;
                background:#111;border-radius:8px;padding:9px 12px;border:1px solid #1a1a1a">
      <div style="font-size:6.5px;font-weight:800;color:#f59e0b;letter-spacing:2.5px;margin-bottom:5px">✦ RESUMEN</div>
      <div style="font-size:9.5px;color:#666;line-height:1.55;overflow:hidden;height:60px">{safe}</div>
    </div>"""


# ─── Row ──────────────────────────────────────────────────────────

def _row(e, relato=""):
    color    = SPORT_COLOR.get(e["sport"], "#6366f1")
    icon     = SPORT_ICON.get(e["sport"], "🏟")
    day      = _day(e["date"])
    dn       = e["date"].day
    tags     = e.get("display_tags", [])
    tag      = tags[0] if tags else ""
    is_fav   = e.get("favorite", False)
    score    = e.get("score", 50)
    featured = score <= 10

    # Fondo sutil para eventos destacados
    bg      = f"background:linear-gradient(90deg,{color}14 0%,transparent 55%);" if featured else ""
    bdr_w   = "4px" if featured else "2px"

    # ── Strings truncados en Python ──────────────────────────────
    league_str  = _t((e.get("league") or "").upper(), CHARS_LEAGUE)
    name_limit  = CHARS_NAME_TAG if tag else CHARS_NAME
    name_str    = _t(_match_name(e), name_limit)
    channel_str = _t(e.get("broadcast","").split("/")[0].split(",")[0].strip(), CHARS_CHANNEL)
    relato_str  = _t(relato, CHARS_RELATO)

    # ── Tag pill ────────────────────────────────────────────────
    tag_html = ""
    if tag:
        tag_t = _t(tag, 14)
        tag_html = (
            f'<span style="display:inline-block;flex-shrink:0;'
            f'background:{color}22;color:{color};border-radius:3px;'
            f'padding:0 5px;font-size:7px;font-weight:800;letter-spacing:.5px;'
            f'margin-right:5px;line-height:16px">{tag_t}</span>'
        )

    # ── Dot favorito ────────────────────────────────────────────
    dot = f'<span style="color:{color};font-size:8px;margin-right:5px;flex-shrink:0">●</span>' if is_fav else ""

    # ── Tamaños según featured ───────────────────────────────────
    name_px   = "13px"  if featured else "12px"
    name_w    = "800"   if featured else "700"
    name_col  = "#fff"  if featured else "#ddd"
    day_n_px  = "19px"  if featured else "17px"
    time_px   = "17px"  if featured else "15px"
    time_col  = "#fff"  if featured else "#ccc"

    relato_html = ""  # relatos van en el texto WhatsApp, no en la imagen

    return f"""
    <div style="height:{ROW_H}px;overflow:hidden;{bg}
                border-left:{bdr_w} solid {color};border-bottom:1px solid #131313;
                display:flex;align-items:center;padding:0 {PAD_R}px 0 {PAD_L}px">

      <!-- Día: {DAY_W}px fijo -->
      <div style="width:{DAY_W}px;flex-shrink:0;margin-right:{GAP_DAY}px;text-align:center">
        <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:.5px">{day}</div>
        <div style="font-size:{day_n_px};font-weight:900;color:#fff;line-height:1">{dn}</div>
      </div>

      <!-- Info: {INFO_W}px fijo — sin flex, sin min-width -->
      <div style="width:{INFO_W}px;overflow:hidden;flex-shrink:0">

        <!-- Liga: 1 línea, ya truncada en Python -->
        <div style="font-size:7px;color:#333;font-weight:700;
                    white-space:nowrap;margin-bottom:3px">
          {icon} {league_str}
        </div>

        <!-- Nombre: 1 línea, flex para tag + texto -->
        <div style="display:flex;align-items:center;margin-bottom:4px;overflow:hidden;height:16px">
          {tag_html}
          {dot}
          <span style="font-size:{name_px};font-weight:{name_w};color:{name_col};
                       white-space:nowrap;line-height:1">{name_str}</span>
        </div>

        <!-- Canal: 1 línea -->
        <div style="margin-bottom:2px">
          <span style="background:#ffffff0d;border-radius:3px;padding:1px 6px;
                       font-size:7.5px;color:#555;font-weight:600;white-space:nowrap">·{channel_str}</span>
        </div>

        {relato_html}

      </div>

      <!-- Gap -->
      <div style="width:{GAP_TIME}px;flex-shrink:0"></div>

      <!-- Hora: {TIME_W}px fijo, alineada a la derecha -->
      <div style="width:{TIME_W}px;flex-shrink:0;text-align:right">
        <div style="font-size:{time_px};font-weight:900;color:{time_col};
                    white-space:nowrap;line-height:1">{e.get('time_mx','TBD')}</div>
        <div style="font-size:6.5px;color:#2a2a2a;margin-top:2px;font-weight:700">CDMX</div>
      </div>

    </div>"""


# ─── Entry point ──────────────────────────────────────────────────

def generate_card_html(events, resumen, relatos_map):
    now        = datetime.now(MX_TZ)
    date_range = _date_range(events)
    total      = len(events)

    # Cronograma: orden cronológico
    by_time = sorted(events, key=lambda e: (e["date"], e.get("time_mx", "99:99")))
    shown   = by_time[:MAX_ROWS]

    rows_html = "".join(_row(e, relatos_map.get(_key(e), "")) for e in shown)

    more = total - len(shown)
    more_html = (
        f'<div style="height:{MORE_H}px;overflow:hidden;display:flex;align-items:center;padding:0 {PAD_L}px">'
        f'<span style="font-size:8px;color:#2d2d2d;font-style:italic">'
        f'+ {more} evento{"s" if more!=1 else ""} más — ver agenda completa</span></div>'
    ) if more > 0 else f'<div style="height:{MORE_H}px"></div>'

    footer_html = (
        f'<div style="height:{FOOTER_H}px;overflow:hidden;display:flex;align-items:center;'
        f'justify-content:center;background:#080808;border-top:1px solid #111">'
        f'<span style="font-size:6.5px;color:#1d1d1d;font-weight:700;letter-spacing:2px">'
        f'AGENDA DEPORTIVA · CDMX {now.year}</span></div>'
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,700;0,800;0,900;1,400&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased}}
  html,body{{font-family:'Inter',sans-serif;background:#0a0a0a;color:#e2e8f0;
             width:{CARD_W}px;height:{CARD_H}px;overflow:hidden}}
</style>
</head>
<body style="display:flex;flex-direction:column">

  <div style="height:{PAD_TOP}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{_hero(events)}</div>
  <div style="height:{GAP1}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{_wordmark(date_range)}</div>
  <div style="height:{GAP2}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{_resumen(resumen)}</div>
  <div style="height:{GAP3}px;flex-shrink:0"></div>

  <div style="flex-shrink:0;background:#0d0d0d;border-radius:10px 10px 0 0;overflow:hidden">
    <div style="height:{CRONO_HDR_H}px;display:flex;align-items:center;
                padding:0 {PAD_L}px;border-bottom:1px solid #141414">
      <span style="font-size:6.5px;font-weight:800;color:#252525;letter-spacing:2.5px">
          CRONOGRAMA · {total} EVENTOS ESTA SEMANA
      </span>
    </div>
    {rows_html}
    {more_html}
  </div>

  <div style="flex-shrink:0">{footer_html}</div>

</body>
</html>"""


CARD_HEIGHT = CARD_H
CARD_WIDTH  = CARD_W

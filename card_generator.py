"""
Card visual fija 390×844px (iPhone 14).
Cada sección tiene altura explícita — nada se corta a mitad.
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

# ── Dimensiones fijas (px) ────────────────────────────────────────
CARD_W      = 390
CARD_H      = 844
HERO_H      = 118   # 2 bloques lado a lado
WORDMARK_H  = 52
RESUMEN_H   = 68
CRONO_HDR_H = 22
ROW_H       = 90    # cada fila de evento
MAX_ROWS    = 5
MORE_H      = 20
FOOTER_H    = 20

# Gaps entre secciones (distribuyen el espacio sobrante)
# Total fijo = 8+118+52+68+22+450+20+20 = 758 → sobrante 86px en gaps
GAP_AFTER_HERO     = 12
GAP_AFTER_WORDMARK = 10
GAP_AFTER_RESUMEN  = 10


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


# ── Hero ──────────────────────────────────────────────────────────
def _hero(events):
    featured = events[:2]
    while len(featured) < 2:
        featured.append(None)

    blocks = []
    for e in featured:
        if e is None:
            blocks.append(f'<div style="flex:1;height:{HERO_H}px"></div>')
            continue

        color = SPORT_COLOR.get(e["sport"], "#6366f1")
        icon  = SPORT_ICON.get(e["sport"], "🏟")
        tags  = e.get("display_tags", [])
        tag   = tags[0] if tags else e["sport"].upper()
        day   = f"{_day(e['date'])} {e['date'].day}"

        if e.get("home_badge"):
            badge = f'<img src="{e["home_badge"]}" style="height:40px;width:40px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.8))">'
        elif e.get("away_badge"):
            badge = f'<img src="{e["away_badge"]}" style="height:40px;width:40px;object-fit:contain">'
        else:
            badge = f'<span style="font-size:2.2rem;line-height:1">{icon}</span>'

        if e.get("away") and e["sport"] == "Fútbol":
            h = " ".join(e["home"].split()[:2])
            a = " ".join(e["away"].split()[:2])
            title = f"{h}<br>vs {a}"
        else:
            raw = e.get("home", "")
            title = raw[:18] if len(raw) <= 18 else raw[:16] + "…"

        blocks.append(f"""
        <div style="flex:1;height:{HERO_H}px;overflow:hidden;
                    background:linear-gradient(145deg,{color}25 0%,#0d0d0d 65%);
                    border-radius:10px;border:1px solid {color}30;
                    padding:10px;box-sizing:border-box;
                    display:flex;flex-direction:column;justify-content:space-between">
          <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:1.5px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              {tag} · {day}
          </div>
          <div style="display:flex;align-items:center;justify-content:center;flex:1;padding:4px 0">
              {badge}
          </div>
          <div style="font-size:10.5px;font-weight:900;color:#fff;line-height:1.2;
                      overflow:hidden;max-height:32px">{title}</div>
          <div style="font-size:9px;font-weight:700;color:#ffe87a;margin-top:3px;white-space:nowrap">
              {e.get('time_mx','TBD')} CDMX
          </div>
        </div>""")

    return (
        f'<div style="display:flex;gap:8px;height:{HERO_H}px;'
        f'padding:0 14px;box-sizing:content-box">{"".join(blocks)}</div>'
    )


# ── Wordmark ──────────────────────────────────────────────────────
def _wordmark(date_range):
    return f"""
    <div style="height:{WORDMARK_H}px;overflow:hidden;text-align:center;
                padding:4px 14px 0;box-sizing:border-box">
      <div style="font-size:20px;font-weight:900;color:#fff;letter-spacing:.5px;line-height:1.1">
          AGENDA DEPORTIVA
      </div>
      <div style="display:inline-flex;align-items:center;gap:5px;margin-top:6px;
                  background:#111;border-radius:20px;padding:3px 12px;border:1px solid #1e1e1e">
        <span style="color:#f59e0b;font-size:7px">✦</span>
        <span style="font-size:7.5px;font-weight:700;color:#444;letter-spacing:2px">
            {date_range} · CDMX
        </span>
        <span style="color:#f59e0b;font-size:7px">✦</span>
      </div>
    </div>"""


# ── Resumen ───────────────────────────────────────────────────────
def _resumen(text):
    safe = text[:220] + "…" if len(text) > 220 else text
    return f"""
    <div style="height:{RESUMEN_H}px;overflow:hidden;margin:0 14px;
                background:#111;border-radius:8px;padding:8px 11px;
                border:1px solid #1a1a1a;box-sizing:border-box">
      <div style="font-size:6.5px;font-weight:800;color:#f59e0b;letter-spacing:2.5px;margin-bottom:4px">
          ✦ RESUMEN
      </div>
      <div style="font-size:9px;color:#666;line-height:1.5;
                  overflow:hidden;height:46px">{safe}</div>
    </div>"""


# ── Fila de evento (altura fija ROW_H) ────────────────────────────
def _row(e, relato=""):
    color  = SPORT_COLOR.get(e["sport"], "#6366f1")
    icon   = SPORT_ICON.get(e["sport"], "🏟")
    day    = _day(e["date"])
    dn     = e["date"].day
    tags   = e.get("display_tags", [])
    tag    = tags[0] if tags else ""
    is_fav = e.get("favorite", False)

    # Nombre del partido
    if e.get("away") and e["sport"] in ("Fútbol", "Rugby"):
        h = " ".join(e["home"].split()[:2])
        a = " ".join(e["away"].split()[:2])
        match_name = f"{h} vs {a}"
    else:
        match_name = e.get("home", "")

    # Canal
    ch = e.get("broadcast", "").split("/")[0].split(",")[0].strip()[:18]

    # Tag pill — inline antes del nombre
    tag_pill = (
        f'<span style="display:inline-block;background:{color}22;color:{color};'
        f'border-radius:3px;padding:0 5px;font-size:7px;font-weight:800;'
        f'letter-spacing:.5px;vertical-align:middle;margin-right:5px">{tag}</span>'
    ) if tag else ""

    fav_dot = f'<span style="color:{color};font-size:8px;margin-right:5px;vertical-align:middle">●</span>' if is_fav else ""

    # Relato — exactamente 1 línea, truncado con CSS
    relato_html = ""
    if relato:
        relato_html = f"""
        <div style="font-size:8px;color:#3d3d3d;font-style:italic;margin-top:4px;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
            "{relato}"
        </div>"""

    return f"""
    <div style="height:{ROW_H}px;overflow:hidden;display:flex;align-items:stretch;
                padding:0 14px;border-bottom:1px solid #131313;border-left:3px solid {color};
                box-sizing:border-box">

      <!-- Día -->
      <div style="width:34px;flex-shrink:0;margin-right:12px;
                  display:flex;flex-direction:column;justify-content:center;align-items:center">
        <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:.5px">{day}</div>
        <div style="font-size:19px;font-weight:900;color:#fff;line-height:1">{dn}</div>
      </div>

      <!-- Info -->
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;
                  overflow:hidden">
        <!-- liga -->
        <div style="font-size:7px;color:#333;font-weight:700;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:3px">
            {icon} {e.get('league','')[:30].upper()}
        </div>
        <!-- nombre — block puro para que el ellipsis funcione -->
        <div style="font-size:12.5px;font-weight:800;color:#fff;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                    display:block;line-height:1.2;margin-bottom:4px">
            {fav_dot}{tag_pill}{match_name}
        </div>
        <!-- canal -->
        <div style="white-space:nowrap;overflow:hidden">
          <span style="background:#ffffff0d;border-radius:3px;padding:1px 6px;
                       font-size:7.5px;color:#555;font-weight:600">·{ch}</span>
        </div>
        {relato_html}
      </div>

      <!-- Hora -->
      <div style="flex-shrink:0;margin-left:12px;
                  display:flex;flex-direction:column;justify-content:center;align-items:flex-end">
        <div style="font-size:17px;font-weight:900;color:#fff;line-height:1;white-space:nowrap">
            {e.get('time_mx','TBD')}
        </div>
        <div style="font-size:6.5px;color:#2a2a2a;margin-top:2px;font-weight:700">CDMX</div>
      </div>

    </div>"""


# ── Entry point ───────────────────────────────────────────────────
def generate_card_html(events, resumen, relatos_map):
    now        = datetime.now(MX_TZ)
    shown      = events[:MAX_ROWS]
    total      = len(events)
    date_range = _date_range(events)

    hero_html     = _hero(events)
    wordmark_html = _wordmark(date_range)
    resumen_html  = _resumen(resumen)
    rows_html     = "".join(_row(e, relatos_map.get(_key(e), "")) for e in shown)

    more = total - len(shown)
    more_html = (
        f'<div style="height:{MORE_H}px;overflow:hidden;display:flex;align-items:center;'
        f'padding:0 14px;"><span style="font-size:8px;color:#2d2d2d;font-style:italic">'
        f'+ {more} evento{"s" if more!=1 else ""} más esta semana</span></div>'
    ) if more > 0 else f'<div style="height:{MORE_H}px"></div>'

    footer_html = (
        f'<div style="height:{FOOTER_H}px;overflow:hidden;display:flex;align-items:center;'
        f'justify-content:center;background:#080808;border-top:1px solid #111">'
        f'<span style="font-size:6.5px;color:#1d1d1d;font-weight:700;letter-spacing:2px">'
        f'AGENDA DEPORTIVA · CDMX {now.year}</span></div>'
    )

    # Verificación de alturas (debug interno)
    total_h = (8 + HERO_H + GAP_AFTER_HERO + WORDMARK_H + GAP_AFTER_WORDMARK +
               RESUMEN_H + GAP_AFTER_RESUMEN + CRONO_HDR_H +
               ROW_H * MAX_ROWS + MORE_H + FOOTER_H)
    # total_h debería ser < 844

    crono_rows_h = ROW_H * MAX_ROWS + MORE_H
    crono_h = CRONO_HDR_H + crono_rows_h

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased}}
  html,body{{
    font-family:'Inter',sans-serif;
    background:#0a0a0a;color:#e2e8f0;
    width:{CARD_W}px;height:{CARD_H}px;
    overflow:hidden;
  }}
</style>
</head>
<body style="display:flex;flex-direction:column">

  <div style="height:8px;flex-shrink:0"></div>

  <!-- Hero: {HERO_H}px -->
  <div style="flex-shrink:0">{hero_html}</div>

  <div style="height:{GAP_AFTER_HERO}px;flex-shrink:0"></div>

  <!-- Wordmark: {WORDMARK_H}px -->
  <div style="flex-shrink:0">{wordmark_html}</div>

  <div style="height:{GAP_AFTER_WORDMARK}px;flex-shrink:0"></div>

  <!-- Resumen: {RESUMEN_H}px -->
  <div style="flex-shrink:0">{resumen_html}</div>

  <div style="height:{GAP_AFTER_RESUMEN}px;flex-shrink:0"></div>

  <!-- Cronograma -->
  <div style="flex-shrink:0;background:#0d0d0d;border-radius:10px 10px 0 0;overflow:hidden">
    <!-- Header: {CRONO_HDR_H}px -->
    <div style="height:{CRONO_HDR_H}px;overflow:hidden;display:flex;align-items:center;
                padding:0 14px;border-bottom:1px solid #141414">
      <span style="font-size:6.5px;font-weight:800;color:#252525;letter-spacing:2.5px">
          CRONOGRAMA · {total} EVENTOS ESTA SEMANA
      </span>
    </div>
    <!-- Rows: {ROW_H * MAX_ROWS}px -->
    {rows_html}
    {more_html}
  </div>

  <!-- Footer: {FOOTER_H}px -->
  <div style="flex-shrink:0">{footer_html}</div>

</body>
</html>"""


# Exportar constante para que screenshot.py use el mismo alto
CARD_HEIGHT = CARD_H
CARD_WIDTH  = CARD_W

"""
Card visual fija 390×844px (iPhone 14).
Cada sección tiene altura explícita garantizada.
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

# ─────────────────────────────────────────────────────────────────
# Dimensiones fijas — todo suma exacto dentro de 844px
# 8 + 116 + 10 + 48 + 8 + 88 + 8 + 22 + (5×98) + 22 + 24 = 844
# ─────────────────────────────────────────────────────────────────
PAD_TOP     = 8
HERO_H      = 116
GAP1        = 10
WORDMARK_H  = 48
GAP2        = 8
RESUMEN_H   = 88   # más espacio para el resumen
GAP3        = 8
CRONO_HDR_H = 22
ROW_H       = 98   # altura fija por evento
MAX_ROWS    = 5
MORE_H      = 22
FOOTER_H    = 24

CARD_W = 390
CARD_H = 844


def _verify():
    t = PAD_TOP+HERO_H+GAP1+WORDMARK_H+GAP2+RESUMEN_H+GAP3+CRONO_HDR_H+ROW_H*MAX_ROWS+MORE_H+FOOTER_H
    assert t <= CARD_H, f"Layout overflow: {t}px > {CARD_H}px"

_verify()


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
    """Siempre muestra los dos equipos si existen."""
    home = e.get("home", "") or ""
    away = e.get("away", "") or ""

    if away:
        # Abreviar si es muy largo: máx 2 palabras por equipo
        h = " ".join(home.split()[:2])
        a = " ".join(away.split()[:2])
        return f"{h} vs {a}"
    return home


# ── Hero: 2 eventos destacados ────────────────────────────────────
def _hero(events):
    # Los 2 con menor score (más importantes), sin importar orden temporal
    top2 = sorted(events, key=lambda e: e.get("score", 99))[:2]
    while len(top2) < 2:
        top2.append(None)

    blocks = []
    for e in top2:
        if e is None:
            blocks.append(f'<div style="flex:1;height:{HERO_H}px"></div>')
            continue

        color = SPORT_COLOR.get(e["sport"], "#6366f1")
        icon  = SPORT_ICON.get(e["sport"], "🏟")
        tags  = e.get("display_tags", [])
        tag   = tags[0] if tags else e["sport"].upper()
        day   = f"{_day(e['date'])} {e['date'].day}"

        if e.get("home_badge"):
            badge = f'<img src="{e["home_badge"]}" style="height:38px;width:38px;object-fit:contain;filter:drop-shadow(0 2px 8px rgba(0,0,0,.9))">'
        elif e.get("away_badge"):
            badge = f'<img src="{e["away_badge"]}" style="height:38px;width:38px;object-fit:contain">'
        else:
            badge = f'<span style="font-size:2.2rem;line-height:1">{icon}</span>'

        name = _match_name(e)
        if len(name) > 22:
            name = name[:20] + "…"

        blocks.append(f"""
        <div style="flex:1;height:{HERO_H}px;overflow:hidden;
                    background:linear-gradient(145deg,{color}28 0%,#0d0d0d 70%);
                    border-radius:10px;border:1px solid {color}35;
                    padding:10px;display:flex;flex-direction:column;justify-content:space-between">
          <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:1.5px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{tag} · {day}</div>
          <div style="display:flex;align-items:center;justify-content:center;flex:1;padding:3px 0">{badge}</div>
          <div style="font-size:10px;font-weight:900;color:#fff;line-height:1.2;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</div>
          <div style="font-size:9px;font-weight:700;color:#ffe87a;margin-top:4px;white-space:nowrap">
              {e.get('time_mx','TBD')} CDMX
          </div>
        </div>""")

    return (
        f'<div style="display:flex;gap:8px;height:{HERO_H}px;padding:0 14px">'
        + "".join(blocks) + "</div>"
    )


# ── Wordmark ──────────────────────────────────────────────────────
def _wordmark(date_range):
    return f"""
    <div style="height:{WORDMARK_H}px;overflow:hidden;text-align:center;
                padding:2px 14px 0">
      <div style="font-size:19px;font-weight:900;color:#fff;letter-spacing:.5px;line-height:1.15">
          AGENDA DEPORTIVA
      </div>
      <div style="display:inline-flex;align-items:center;gap:5px;margin-top:5px;
                  background:#111;border-radius:20px;padding:3px 12px;border:1px solid #1e1e1e">
        <span style="color:#f59e0b;font-size:7px">✦</span>
        <span style="font-size:7.5px;font-weight:700;color:#444;letter-spacing:2px">{date_range} · CDMX</span>
        <span style="color:#f59e0b;font-size:7px">✦</span>
      </div>
    </div>"""


# ── Resumen ───────────────────────────────────────────────────────
def _resumen(text):
    return f"""
    <div style="height:{RESUMEN_H}px;overflow:hidden;margin:0 14px;
                background:#111;border-radius:8px;padding:9px 12px;border:1px solid #1a1a1a">
      <div style="font-size:6.5px;font-weight:800;color:#f59e0b;letter-spacing:2.5px;margin-bottom:5px">✦ RESUMEN</div>
      <div style="font-size:9.5px;color:#666;line-height:1.55;overflow:hidden;height:56px">{text}</div>
    </div>"""


# ── Fila de evento — altura fija ROW_H, todo en 1 línea ──────────
def _row(e, relato=""):
    color  = SPORT_COLOR.get(e["sport"], "#6366f1")
    icon   = SPORT_ICON.get(e["sport"], "🏟")
    day    = _day(e["date"])
    dn     = e["date"].day
    tags   = e.get("display_tags", [])
    tag    = tags[0] if tags else ""
    is_fav = e.get("favorite", False)
    score  = e.get("score", 50)

    # Fondo destacado para eventos importantes (score <= 10)
    is_featured = score <= 10
    bg = f"background:linear-gradient(90deg,{color}12 0%,transparent 60%);" if is_featured else ""
    border_w = "4px" if is_featured else "3px"

    # Nombre: siempre los dos equipos, 1 sola línea, ellipsis
    name = _match_name(e)

    # Liga — corta y en mayúsculas
    league = e.get("league", "")[:26].upper()

    # Tag pill
    tag_html = (
        f'<span style="display:inline-block;background:{color}22;color:{color};'
        f'border-radius:3px;padding:0 5px;font-size:7px;font-weight:800;'
        f'letter-spacing:.5px;margin-right:6px;vertical-align:middle;flex-shrink:0">{tag}</span>'
    ) if tag else ""

    # Canal
    ch = e.get("broadcast", "").split("/")[0].split(",")[0].strip()[:16]

    # Relato — 1 línea exacta, ellipsis, no wrapping
    relato_html = ""
    if relato:
        relato_html = f"""
        <div style="height:14px;overflow:hidden;margin-top:3px">
          <div style="font-size:8px;color:#3a3a3a;font-style:italic;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">"{relato}"</div>
        </div>"""

    # Nombre del partido — 1 línea, font más grande si es featured
    name_size = "13.5px" if is_featured else "12.5px"
    name_color = "#fff" if is_featured else "#e0e0e0"
    fav_dot = f'<span style="color:{color};font-size:8px;margin-right:5px;vertical-align:middle">●</span>' if is_fav else ""

    return f"""
    <div style="height:{ROW_H}px;overflow:hidden;display:flex;align-items:stretch;
                padding:0 14px;border-bottom:1px solid #131313;
                border-left:{border_w} solid {color};{bg}">

      <!-- Día: columna fija -->
      <div style="width:34px;flex-shrink:0;margin-right:12px;
                  display:flex;flex-direction:column;justify-content:center;align-items:center">
        <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:.5px">{day}</div>
        <div style="font-size:{'20' if is_featured else '18'}px;font-weight:900;color:#fff;line-height:1">{dn}</div>
      </div>

      <!-- Info: flex-1, overflow hidden, todo en 1 línea por elemento -->
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;overflow:hidden">

        <!-- liga: 1 línea -->
        <div style="height:12px;overflow:hidden;margin-bottom:3px">
          <div style="font-size:7px;color:#333;font-weight:700;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              {icon} {league}
          </div>
        </div>

        <!-- tag + nombre: 1 línea -->
        <div style="height:18px;overflow:hidden;display:flex;align-items:center;margin-bottom:4px">
          {tag_html}
          <div style="font-size:{name_size};font-weight:{'900' if is_featured else '800'};
                      color:{name_color};white-space:nowrap;overflow:hidden;
                      text-overflow:ellipsis;flex:1;min-width:0">
              {fav_dot}{name}
          </div>
        </div>

        <!-- canal: 1 línea -->
        <div style="height:16px;overflow:hidden;margin-bottom:2px">
          <span style="background:#ffffff0d;border-radius:3px;padding:1px 6px;
                       font-size:7.5px;color:#555;font-weight:600">·{ch}</span>
        </div>

        {relato_html}

      </div>

      <!-- Hora: columna fija -->
      <div style="flex-shrink:0;margin-left:10px;
                  display:flex;flex-direction:column;justify-content:center;align-items:flex-end">
        <div style="font-size:{'18' if is_featured else '16'}px;font-weight:900;
                    color:{'#fff' if is_featured else '#ddd'};line-height:1;white-space:nowrap">
            {e.get('time_mx','TBD')}
        </div>
        <div style="font-size:6.5px;color:#2a2a2a;margin-top:2px;font-weight:700">CDMX</div>
      </div>

    </div>"""


# ── Entry point ───────────────────────────────────────────────────
def generate_card_html(events, resumen, relatos_map):
    now        = datetime.now(MX_TZ)
    date_range = _date_range(events)
    total      = len(events)

    # Ordenar por fecha y hora para el cronograma
    sorted_events = sorted(events, key=lambda e: (e["date"], e.get("time_mx", "99:99")))
    shown = sorted_events[:MAX_ROWS]

    hero_html     = _hero(events)   # hero usa los top por score, no por fecha
    wordmark_html = _wordmark(date_range)
    resumen_html  = _resumen(resumen)
    rows_html     = "".join(_row(e, relatos_map.get(_key(e), "")) for e in shown)

    more = total - len(shown)
    more_html = (
        f'<div style="height:{MORE_H}px;overflow:hidden;display:flex;align-items:center;padding:0 14px">'
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
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased}}
  html,body{{font-family:'Inter',sans-serif;background:#0a0a0a;color:#e2e8f0;
             width:{CARD_W}px;height:{CARD_H}px;overflow:hidden}}
</style>
</head>
<body style="display:flex;flex-direction:column">

  <div style="height:{PAD_TOP}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{hero_html}</div>
  <div style="height:{GAP1}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{wordmark_html}</div>
  <div style="height:{GAP2}px;flex-shrink:0"></div>
  <div style="flex-shrink:0">{resumen_html}</div>
  <div style="height:{GAP3}px;flex-shrink:0"></div>

  <div style="flex-shrink:0;background:#0d0d0d;border-radius:10px 10px 0 0;overflow:hidden">
    <div style="height:{CRONO_HDR_H}px;overflow:hidden;display:flex;align-items:center;
                padding:0 14px;border-bottom:1px solid #141414">
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

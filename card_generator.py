"""
Card visual 390×844px (iPhone 14) — texto sin cortar, layout compacto.
"""
from datetime import datetime, timedelta
import pytz

TIMEZONE = "America/Mexico_City"
MX_TZ    = pytz.timezone(TIMEZONE)

DAY_ES = {
    "Monday":"LUN","Tuesday":"MAR","Wednesday":"MIÉ",
    "Thursday":"JUE","Friday":"VIE","Saturday":"SÁB","Sunday":"DOM"
}
MONTH_ES = {
    1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
    7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"
}

SPORT_COLOR = {
    "Fútbol":"#22c55e","Fórmula 1":"#ef4444",
    "NBA":"#f97316","Tenis":"#f59e0b","Rugby":"#8b5cf6",
}
SPORT_ICON = {
    "Fútbol":"⚽","Fórmula 1":"🏎","NBA":"🏀","Tenis":"🎾","Rugby":"🏉",
}


def _day_label(date):
    return DAY_ES.get(date.strftime("%A"), date.strftime("%a").upper())


def _date_range(events):
    if not events:
        return ""
    dates = sorted(set(e["date"] for e in events))
    s, en = dates[0], dates[-1]
    if s.month == en.month:
        return f"{s.day}–{en.day} {MONTH_ES[s.month].upper()} {s.year}"
    return f"{s.day} {MONTH_ES[s.month][:3].upper()} – {en.day} {MONTH_ES[en.month][:3].upper()} {s.year}"


def _event_key(e):
    return f"{e.get('home','')}_{e.get('away','')}_{e['date']}"


# ── Selección de eventos para la card ────────────────────────────
def select_card_events(events, max_events=5):
    """Toma los ya filtrados/ordenados por relevance.py y limita a max."""
    return events[:max_events]


# ── Hero (2 bloques superiores) ──────────────────────────────────
def _hero(events):
    # Los 2 eventos con menor score (más importantes)
    featured = events[:2]
    while len(featured) < 2:
        featured.append(None)

    blocks = []
    for e in featured:
        if e is None:
            blocks.append('<div style="flex:1"></div>')
            continue

        color = SPORT_COLOR.get(e["sport"], "#6366f1")
        icon  = SPORT_ICON.get(e["sport"], "🏟")
        day   = f"{_day_label(e['date'])} {e['date'].day}"
        tags  = e.get("display_tags", [])
        tag   = tags[0] if tags else e["sport"].upper()

        # Logo / badge
        if e.get("home_badge"):
            media = f'<img src="{e["home_badge"]}" style="height:44px;width:44px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,.7))">'
        elif e.get("away_badge"):
            media = f'<img src="{e["away_badge"]}" style="height:44px;width:44px;object-fit:contain">'
        else:
            media = f'<div style="font-size:2rem;line-height:1">{icon}</div>'

        # Nombre corto
        if e.get("away") and e["sport"] == "Fútbol":
            h = " ".join(e["home"].split()[:2])
            a = " ".join(e["away"].split()[:2])
            title = f"{h}<br>vs {a}"
        else:
            h = e.get("home","")
            title = "<br>".join(h[i:i+14] for i in range(0, min(len(h),28), 14))

        blocks.append(f"""
        <div style="flex:1;background:linear-gradient(145deg,{color}28 0%,#0d0d0d 70%);
                    border-radius:10px;border:1px solid {color}35;padding:10px 10px 8px;
                    display:flex;flex-direction:column;gap:4px">
          <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:1.5px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{tag} · {day}</div>
          <div style="display:flex;align-items:center;gap:8px;flex:1">
            {media}
            <div style="font-size:11px;font-weight:900;color:#fff;line-height:1.2;
                        overflow:hidden">{title}</div>
          </div>
          <div style="font-size:10px;font-weight:700;color:#fff99a;white-space:nowrap">
              {e.get('time_mx','TBD')} CDMX
          </div>
        </div>""")

    return f'<div style="display:flex;gap:7px;margin-bottom:12px;padding:0 14px">{"".join(blocks)}</div>'


# ── Fila de evento ────────────────────────────────────────────────
def _row(e, relato=""):
    color  = SPORT_COLOR.get(e["sport"], "#6366f1")
    icon   = SPORT_ICON.get(e["sport"], "🏟")
    day    = _day_label(e["date"])
    dn     = e["date"].day
    tags   = e.get("display_tags", [])
    tag    = tags[0] if tags else ""
    is_fav = e.get("favorite", False)

    # Nombre del partido — construido para que el ellipsis funcione en bloque
    if e.get("away") and e["sport"] in ("Fútbol", "Rugby"):
        h = " ".join(e["home"].split()[:2])
        a = " ".join(e["away"].split()[:2])
        match_line = f"{h} vs {a}"
    else:
        match_line = e.get("home", "")

    # Canal — primer valor antes de / o ,
    ch = e.get("broadcast", "").split("/")[0].split(",")[0].strip()[:16]
    ch_html = (
        f'<span style="background:#ffffff0f;border-radius:3px;padding:1px 6px;'
        f'font-size:7.5px;color:#666;font-weight:600">·{ch}</span>'
    ) if ch else ""

    # Tag de relevancia — sobre el nombre del partido (línea separada)
    tag_html = (
        f'<span style="display:inline-block;background:{color}22;color:{color};'
        f'border-radius:3px;padding:1px 5px;font-size:7px;font-weight:800;'
        f'letter-spacing:.5px;margin-bottom:3px">{tag}</span>'
    ) if tag else ""

    fav_dot = f'<span style="color:{color};font-size:7px;margin-right:4px">●</span>' if is_fav else ""

    # Relato — 2 líneas máximo, text-overflow en elemento bloque con width fijo
    relato_html = ""
    if relato:
        r = relato[:100] + "…" if len(relato) > 100 else relato
        relato_html = (
            f'<div style="font-size:8px;color:#4a4a4a;font-style:italic;margin-top:3px;'
            f'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;'
            f'overflow:hidden;line-height:1.35">"{r}"</div>'
        )

    return f"""
    <div style="display:flex;align-items:stretch;padding:9px 14px;
                border-bottom:1px solid #141414;border-left:3px solid {color}">
      <!-- día -->
      <div style="width:34px;flex-shrink:0;margin-right:11px;padding-top:1px">
        <div style="font-size:7px;font-weight:800;color:{color};letter-spacing:.5px;text-align:center">{day}</div>
        <div style="font-size:18px;font-weight:900;color:#fff;line-height:1;text-align:center">{dn}</div>
      </div>
      <!-- info — bloque con ancho fijo para que el ellipsis funcione -->
      <div style="flex:1;min-width:0">
        <!-- liga -->
        <div style="font-size:7px;color:#3a3a3a;font-weight:700;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px">
            {icon} {e.get('league','')[:28].upper()}
        </div>
        <!-- tag encima del nombre -->
        {tag_html}
        <!-- nombre partido: bloque, no flex → ellipsis funciona -->
        <div style="font-size:12.5px;font-weight:800;color:#fff;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                    display:block;line-height:1.2">
            {fav_dot}{match_line}
        </div>
        <!-- canal -->
        <div style="margin-top:4px">{ch_html}</div>
        {relato_html}
      </div>
      <!-- hora — alineada al centro verticalmente -->
      <div style="flex-shrink:0;margin-left:10px;display:flex;flex-direction:column;
                  justify-content:center;align-items:flex-end">
        <div style="font-size:16px;font-weight:900;color:#fff;line-height:1;white-space:nowrap">
            {e.get('time_mx','TBD')}
        </div>
        <div style="font-size:6.5px;color:#2e2e2e;margin-top:2px;font-weight:700">CDMX</div>
      </div>
    </div>"""


# ── Entry point ───────────────────────────────────────────────────
def generate_card_html(events, resumen, relatos_map):
    today      = datetime.now(MX_TZ)
    shown      = select_card_events(events, max_events=5)
    total      = len(events)
    date_range = _date_range(events)

    hero = _hero(events)
    rows = "".join(_row(e, relatos_map.get(_event_key(e),"")) for e in shown)

    resumen_trim = resumen[:200] + "…" if len(resumen) > 200 else resumen

    more = total - len(shown)
    more_html = (
        f'<div style="padding:6px 14px;font-size:8px;color:#333;font-style:italic">'
        f'+ {more} evento{"s" if more!=1 else ""} más — ver agenda completa</div>'
    ) if more > 0 else ""

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
    width:390px;height:844px;overflow:hidden;
  }}
</style>
</head>
<body style="display:flex;flex-direction:column">

  <!-- padding top -->
  <div style="height:12px;flex-shrink:0"></div>

  <!-- hero -->
  {hero}

  <!-- wordmark -->
  <div style="text-align:center;padding:0 14px 8px;flex-shrink:0">
    <div style="font-size:22px;font-weight:900;color:#fff;letter-spacing:1px;line-height:1">
        AGENDA DEPORTIVA
    </div>
    <div style="display:inline-flex;align-items:center;gap:5px;margin-top:5px;
                background:#111;border-radius:20px;padding:3px 11px;border:1px solid #1c1c1c">
      <span style="color:#f59e0b;font-size:7px">✦</span>
      <span style="font-size:7.5px;font-weight:700;color:#444;letter-spacing:2px;text-transform:uppercase">
          {date_range} · CDMX
      </span>
      <span style="color:#f59e0b;font-size:7px">✦</span>
    </div>
  </div>

  <!-- resumen -->
  <div style="margin:0 14px 8px;background:#111;border-radius:8px;padding:9px 11px;
              border:1px solid #1a1a1a;flex-shrink:0">
    <div style="font-size:6.5px;font-weight:800;color:#f59e0b;letter-spacing:2.5px;margin-bottom:4px">✦ RESUMEN</div>
    <div style="font-size:9px;color:#777;line-height:1.5;overflow:hidden;
                display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical">
        {resumen_trim}
    </div>
  </div>

  <!-- cronograma -->
  <div style="background:#0d0d0d;border-radius:10px 10px 0 0;flex:1;
              display:flex;flex-direction:column;overflow:hidden;margin:0 0 0 0">
    <div style="padding:7px 14px 5px;border-bottom:1px solid #141414;flex-shrink:0">
      <span style="font-size:6.5px;font-weight:800;color:#2a2a2a;letter-spacing:2.5px">
          CRONOGRAMA · {total} EVENTOS ESTA SEMANA
      </span>
    </div>
    <div style="flex:1;overflow:hidden">
      {rows}
      {more_html}
    </div>
  </div>

  <!-- footer -->
  <div style="background:#080808;padding:5px 14px;text-align:center;flex-shrink:0">
    <span style="font-size:6.5px;color:#1e1e1e;font-weight:700;letter-spacing:2px">🏟 KOLEOS SPORTS · CDMX {today.year}</span>
  </div>

</body>
</html>"""

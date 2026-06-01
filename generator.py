from datetime import datetime, timedelta
import pytz
from config import GROUP_NAME, TIMEZONE

MX_TZ = pytz.timezone(TIMEZONE)

SPORT_EMOJI = {
    "Fútbol": "⚽",
    "Fórmula 1": "🏎️",
    "Tenis": "🎾",
    "NBA": "🏀",
}

SPORT_COLOR = {
    "Fútbol": "#22c55e",
    "Fórmula 1": "#ef4444",
    "Tenis": "#f59e0b",
    "NBA": "#f97316",
}

DAY_ES = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}

MONTH_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}


def _day_label(date):
    today = datetime.now(MX_TZ).date()
    if date == today:
        return "Hoy"
    if date == today + timedelta(days=1):
        return "Mañana"
    day_en = date.strftime("%A")
    return DAY_ES.get(day_en, day_en)


def _format_date(date):
    day_en = date.strftime("%A")
    return f"{DAY_ES.get(day_en, day_en)} {date.day} de {MONTH_ES[date.month]}"


def _event_card(event):
    sport = event["sport"]
    emoji = SPORT_EMOJI.get(sport, "🏟️")
    color = SPORT_COLOR.get(sport, "#6366f1")
    favorite_badge = '<span class="fav-badge">★ DESTACADO</span>' if event.get("favorite") else ""

    home_img = f'<img src="{event["home_badge"]}" class="team-badge" onerror="this.style.display=\'none\'">' if event.get("home_badge") else ""
    away_img = f'<img src="{event["away_badge"]}" class="team-badge" onerror="this.style.display=\'none\'">' if event.get("away_badge") else ""

    if event.get("away") and event["sport"] == "Fútbol":
        matchup = f"""
        <div class="matchup">
            {home_img}<span class="team-name">{event['home']}</span>
            <span class="vs">vs</span>
            <span class="team-name">{event['away']}</span>{away_img}
        </div>"""
    else:
        matchup = f'<div class="matchup"><span class="team-name">{event["home"]}</span></div>'
        if event.get("away"):
            matchup = f'<div class="matchup"><span class="team-name">{event["home"]}</span><br><small style="color:#94a3b8">{event["away"]}</small></div>'

    return f"""
    <div class="event-card {'event-favorite' if event.get('favorite') else ''}">
        <div class="event-header" style="border-left: 4px solid {color}">
            <span class="sport-tag" style="background:{color}20; color:{color}">{emoji} {sport}</span>
            {favorite_badge}
        </div>
        <div class="event-league">{event['league']}</div>
        {matchup}
        <div class="event-footer">
            <span class="event-time">🕐 {event['time_mx']} (CDMX)</span>
            <span class="event-broadcast">📺 {event['broadcast']}</span>
        </div>
    </div>"""


def _group_by_day(events):
    days = {}
    for e in events:
        d = e["date"]
        if d not in days:
            days[d] = []
        days[d].append(e)
    return dict(sorted(days.items()))


def _day_section(date, events):
    label = _day_label(date)
    full_date = _format_date(date)
    cards = "\n".join(_event_card(e) for e in events)
    is_today = label == "Hoy"
    today_class = "today-section" if is_today else ""
    return f"""
    <div class="day-section {today_class}">
        <div class="day-header">
            <span class="day-label">{label}</span>
            <span class="day-full">{full_date}</span>
            <span class="event-count">{len(events)} evento{'s' if len(events) != 1 else ''}</span>
        </div>
        <div class="events-grid">
            {cards}
        </div>
    </div>"""


def _whatsapp_text(events_today, events_week):
    today = datetime.now(MX_TZ).date()
    lines = [f"🗓️ *Agenda deportiva — {_format_date(today)}*\n"]

    if events_today:
        lines.append("*HOY:*")
        for e in events_today:
            emoji = SPORT_EMOJI.get(e["sport"], "🏟️")
            star = "⭐ " if e.get("favorite") else ""
            if e["sport"] == "Fútbol" and e.get("away"):
                lines.append(f"{emoji} {star}{e['home']} vs {e['away']} — {e['time_mx']} — {e['broadcast']}")
            else:
                lines.append(f"{emoji} {star}{e['home']} — {e['time_mx']} — {e['broadcast']}")
    else:
        lines.append("Sin eventos hoy 🙈")

    if events_week:
        lines.append("\n*Esta semana:*")
        days = _group_by_day(events_week)
        for date, evs in days.items():
            if date == today:
                continue
            label = _day_label(date)
            lines.append(f"\n_{label}_")
            for e in evs:
                emoji = SPORT_EMOJI.get(e["sport"], "🏟️")
                star = "⭐ " if e.get("favorite") else ""
                if e["sport"] == "Fútbol" and e.get("away"):
                    lines.append(f"  {emoji} {star}{e['home']} vs {e['away']}")
                else:
                    lines.append(f"  {emoji} {star}{e['home']}")

    lines.append("\n📅 Agenda completa: [VER ONLINE]")
    return "\n".join(lines)


CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    min-height: 100vh;
}
.header {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
    padding: 2rem;
    text-align: center;
    border-bottom: 1px solid #1e293b;
}
.header h1 { font-size: 2rem; font-weight: 800; color: #fff; }
.header h1 span { color: #3b82f6; }
.header .subtitle { color: #94a3b8; margin-top: 0.5rem; font-size: 0.95rem; }
.header .updated { color: #64748b; font-size: 0.8rem; margin-top: 0.3rem; }
.tabs {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    padding: 1.5rem 1rem 0;
    border-bottom: 1px solid #1e293b;
}
.tab-btn {
    padding: 0.6rem 1.5rem;
    border: none;
    background: transparent;
    color: #64748b;
    font-size: 0.95rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}
.tab-btn.active { color: #3b82f6; border-bottom-color: #3b82f6; }
.tab-content { display: none; padding: 1.5rem 1rem 3rem; max-width: 900px; margin: 0 auto; }
.tab-content.active { display: block; }
.day-section { margin-bottom: 2rem; }
.day-section.today-section .day-header { border-left-color: #3b82f6; }
.day-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1rem;
    background: #1e293b;
    border-radius: 8px;
    margin-bottom: 1rem;
    border-left: 3px solid #334155;
}
.day-label { font-size: 1.1rem; font-weight: 700; color: #fff; }
.day-full { color: #94a3b8; font-size: 0.85rem; }
.event-count { margin-left: auto; color: #64748b; font-size: 0.8rem; }
.events-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
}
.event-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #334155;
    transition: transform 0.15s;
}
.event-card:hover { transform: translateY(-2px); border-color: #475569; }
.event-favorite { border-color: #f59e0b44; background: #1e293b; }
.event-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.sport-tag {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
}
.fav-badge {
    font-size: 0.65rem;
    color: #f59e0b;
    font-weight: 700;
    margin-left: auto;
}
.event-league { font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem; }
.matchup {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}
.team-badge { width: 24px; height: 24px; object-fit: contain; }
.team-name { font-weight: 600; font-size: 0.9rem; color: #e2e8f0; }
.vs { color: #64748b; font-size: 0.8rem; padding: 0 0.25rem; }
.event-footer { display: flex; flex-direction: column; gap: 0.25rem; }
.event-time { font-size: 0.8rem; color: #94a3b8; }
.event-broadcast { font-size: 0.8rem; color: #60a5fa; }
.whatsapp-box {
    background: #1e293b;
    border-radius: 10px;
    padding: 1.5rem;
    border: 1px solid #334155;
    margin-bottom: 1rem;
}
.whatsapp-box h3 { color: #25d366; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.whatsapp-text {
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    color: #cbd5e1;
    white-space: pre-wrap;
    background: #0f172a;
    padding: 1rem;
    border-radius: 6px;
}
.copy-btn {
    margin-top: 0.75rem;
    padding: 0.5rem 1.25rem;
    background: #25d366;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
}
.copy-btn:hover { background: #1da851; }
.empty-state { text-align: center; padding: 3rem; color: #64748b; }
.empty-state .emoji { font-size: 3rem; margin-bottom: 1rem; }
"""

JS = """
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('.tab-btn[data-tab="' + tab + '"]').classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
}
function copyWhatsapp(id) {
    const text = document.getElementById(id).innerText;
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        btn.textContent = '✓ Copiado!';
        setTimeout(() => btn.textContent = '📋 Copiar para WhatsApp', 1500);
    });
}
"""


def generate_html(all_events):
    now_mx = datetime.now(MX_TZ)
    today = now_mx.date()

    events_today = [e for e in all_events if e["date"] == today]
    events_week = sorted(all_events, key=lambda x: (x["date"], x.get("time_mx", "")))

    # Secciones por día
    days_today = _group_by_day(events_today)
    days_week = _group_by_day(events_week)

    today_sections = "\n".join(_day_section(d, evs) for d, evs in days_today.items()) if days_today else \
        '<div class="empty-state"><div class="emoji">😴</div><p>Sin eventos deportivos hoy.<br>Aprovechá para salir a correr.</p></div>'

    week_sections = "\n".join(_day_section(d, evs) for d, evs in days_week.items()) if days_week else \
        '<div class="empty-state"><div class="emoji">📆</div><p>Sin eventos esta semana.</p></div>'

    # Texto WhatsApp
    wa_today = _whatsapp_text(events_today, [])
    wa_week = _whatsapp_text(events_today, events_week)

    updated = now_mx.strftime("%d/%m/%Y %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agenda Deportiva — {GROUP_NAME}</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="header">
        <h1>🏟️ Agenda <span>Deportiva</span></h1>
        <div class="subtitle">Fútbol · F1 · Tenis · NBA — Todo en horario México</div>
        <div class="updated">Actualizado: {updated} CDMX</div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" data-tab="hoy" onclick="switchTab('hoy')">Hoy ({len(events_today)})</button>
        <button class="tab-btn" data-tab="semana" onclick="switchTab('semana')">Esta semana ({len(events_week)})</button>
        <button class="tab-btn" data-tab="whatsapp" onclick="switchTab('whatsapp')">📱 WhatsApp</button>
    </div>

    <div id="tab-hoy" class="tab-content active">
        {today_sections}
    </div>

    <div id="tab-semana" class="tab-content">
        {week_sections}
    </div>

    <div id="tab-whatsapp" class="tab-content">
        <div class="whatsapp-box">
            <h3>📱 Agenda del día</h3>
            <div class="whatsapp-text" id="wa-today">{wa_today}</div>
            <button class="copy-btn" onclick="copyWhatsapp('wa-today')">📋 Copiar para WhatsApp</button>
        </div>
        <div class="whatsapp-box">
            <h3>📅 Agenda de la semana</h3>
            <div class="whatsapp-text" id="wa-week">{wa_week}</div>
            <button class="copy-btn" onclick="copyWhatsapp('wa-week')">📋 Copiar para WhatsApp</button>
        </div>
    </div>

    <script>{JS}</script>
</body>
</html>"""

    return html

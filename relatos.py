"""
Genera relatos personalizados por evento para el grupo Koleos.
Si ANTHROPIC_API_KEY está en el entorno → usa Claude API.
Si no → genera el prompt para pegar en Claude.ai y guarda la respuesta en relatos_manual.json.
"""
import os
import json
from datetime import datetime
import pytz

TIMEZONE = "America/Mexico_City"
MX_TZ = pytz.timezone(TIMEZONE)

# Contexto del grupo para el prompt
GROUP_CONTEXT = """
Somos 4 amigos argentinos viviendo en Ciudad de México. El grupo se llama Koleos.
- Ger: hincha de River. Organiza los planes, le encanta la F1.
- Manuel (Manu): hincha de Boca. Organiza cenas de F1, muy competitivo con las apuestas.
- Guillo: hincha de River. Juega pádel y tenis, le dice la verdad a todos.
- Nacho (Rama): hincha de Estudiantes. Trabaja mucho, se pierde varios partidos.

Dinámica del grupo: se cargan todo el tiempo (sobre todo Manu por ser de Boca), hacen apuestas, organizan "eventos Koleos" para ver partidos juntos, y siempre hay alguien que se queja de madrugar para la F1.

El tono es: irónico, cálido, muy rioplatense, con referencias internas del grupo.
"""

RELATO_MANUAL_FILE = os.path.join(os.path.dirname(__file__), "relatos_manual.json")


def _build_prompt(events):
    events_text = "\n".join([
        f"- {e['sport']} | {e['league']} | {e.get('home','')} {'vs ' + e['away'] if e.get('away') else ''} | {e['date']} {e['time_mx']} CDMX"
        for e in events
    ])

    prompt = f"""Contexto del grupo:
{GROUP_CONTEXT}

Generá un relato corto (máximo 2 oraciones, tono irónico y cálido) para cada uno de estos eventos deportivos.
El relato debe referenciar al grupo, hacer alguna broma interna, mencionar quién tiene más interés en el evento, y crear anticipación.

Eventos:
{events_text}

Respondé SOLO con un JSON válido, sin markdown, en este formato exacto:
{{
  "resumen_semana": "Párrafo de 3-4 oraciones presentando la semana deportiva, con tono narrativo y referencias al grupo.",
  "relatos": [
    {{"evento": "Nombre del evento", "relato": "El relato corto aquí."}},
    ...
  ]
}}"""
    return prompt


def _try_claude_api(events):
    """Intenta usar Claude API si hay API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = _build_prompt(events)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"  [Claude API] Error: {e}")
        return None


def _load_manual_relatos(events):
    """Carga relatos previamente generados desde archivo."""
    if not os.path.exists(RELATO_MANUAL_FILE):
        return None
    try:
        with open(RELATO_MANUAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _match_relato(event, relatos_list):
    """Busca el relato correspondiente a un evento."""
    home = event.get("home", "").lower()
    away = event.get("away", "").lower()
    sport = event.get("sport", "").lower()
    for r in relatos_list:
        ev_name = r.get("evento", "").lower()
        if home in ev_name or away in ev_name or sport in ev_name:
            return r.get("relato", "")
    return ""


def _fallback_relatos(events):
    """Templates de relatos cuando no hay IA disponible."""
    relatos = {}
    for e in events:
        sport = e["sport"]
        home = e.get("home", "")
        away = e.get("away", "")
        league = e.get("league", "")
        is_fav = e.get("favorite", False)
        key = f"{home}_{away}_{e['date']}"

        if sport == "Fórmula 1":
            label = home  # "CARRERA", "Clasificación", etc.
            if "CARRERA" in label.upper():
                relatos[key] = "Manu viene bancando a Colap desde el día uno. El sábado a las 22 se abre el millón — ¿quién tiene razón?"
            elif "Clasificación" in label or "Clasificación" in label:
                relatos[key] = "Guillo apostó que Colap no suma puntos. El viernes a las 23 se define la grilla — alguien va a tener que justificarse."
            else:
                relatos[key] = f"F1 en vivo. {label} — para los que no tienen miedo de madrugar o trasnochar."
        elif sport == "NBA":
            if "Finals" in league or "Playoffs" in league:
                relatos[key] = f"NBA Finals en casa. {home} vs {away} — Rama dice que lo ve pero siempre se duerme en el tercer cuarto."
            else:
                relatos[key] = f"{home} vs {away}. El básquet de fondo mientras alguien cocina."
        elif sport == "Fútbol":
            if is_fav and ("River" in home or "River" in away):
                relatos[key] = "El partido de los 3 del grupo que saben de fútbol. Manu puede mirarlo pero sin opinar."
            elif is_fav and ("Boca" in home or "Boca" in away):
                relatos[key] = "El partido de Manu. Los demás lo van a mirar igual para poder cargarlo después."
            elif "Libertadores" in league or "Sudamericana" in league:
                relatos[key] = "Copa continental. Siempre hay algún argentino involucrado — el grupo va a tener una opinión."
            elif "Champions" in league:
                relatos[key] = "Champions en modo cine. Ger dijo que ponía la pantalla grande — por confirmar."
            else:
                relatos[key] = f"{home} vs {away}. Partido de fondo, pero alguno siempre termina mirándolo."
        else:
            relatos[key] = f"{home} {'vs ' + away if away else ''} — en agenda por si hay tiempo."

    return relatos


def generate_prompt_file(events):
    """Genera un archivo .txt con el prompt para pegar en Claude.ai."""
    prompt = _build_prompt(events)
    prompt_file = os.path.join(os.path.dirname(__file__), "prompt_para_claude.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    return prompt_file


def save_manual_response(json_text):
    """Guarda la respuesta de Claude.ai en el archivo de relatos manuales."""
    data = json.loads(json_text)
    with open(RELATO_MANUAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Relatos guardados en {RELATO_MANUAL_FILE}")


def get_relatos(events):
    """
    Retorna: (resumen_semana: str, relatos_map: dict[key -> relato])
    Prioridad: Claude API > relatos_manual.json > templates.
    """
    result = None

    # 1. Intentar Claude API
    result = _try_claude_api(events)
    if result:
        print("  ✓ Relatos generados con Claude API")

    # 2. Intentar archivo manual
    if not result:
        result = _load_manual_relatos(events)
        if result:
            print("  ✓ Relatos cargados desde relatos_manual.json")

    if result:
        relatos_list = result.get("relatos", [])
        relatos_map = {}
        for e in events:
            key = f"{e.get('home','')}_{e.get('away','')}_{e['date']}"
            relatos_map[key] = _match_relato(e, relatos_list)
        return result.get("resumen_semana", ""), relatos_map

    # 3. Templates fallback
    print("  ℹ️  Usando relatos por template (sin Claude API)")
    print(f"     Para relatos personalizados: generá el prompt con python3 generate_prompt.py")
    relatos_map = _fallback_relatos(events)
    resumen = (
        f"Semana deportiva cargada para el grupo. "
        f"Hay {len([e for e in events if e['sport'] == 'Fútbol'])} partidos de fútbol, "
        f"F1 en agenda y NBA de fondo. "
        f"Como siempre, alguien va a llegar tarde y alguien no va a poder. "
        f"Pero la agenda está, sin excusas."
    )
    return resumen, relatos_map

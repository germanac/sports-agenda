#!/usr/bin/env python3
"""
Sports Agenda — Koleos
Genera:
  1. docs/index.html   → agenda semanal completa (GitHub Pages)
  2. docs/card.html    → card visual iPhone 14
  3. docs/agenda_koleos.png → imagen para compartir en WhatsApp

Uso:
  python3 main.py          → genera todo
  python3 main.py --no-png → solo HTML (sin Playwright)
  python3 push.py          → genera + git push
"""

import os
import sys
from datetime import datetime
import pytz

from config import TIMEZONE, TRACK_F1, TRACK_NBA, TRACK_TENNIS
from fetchers.espn import fetch_week as fetch_espn
from fetchers.f1 import fetch_week_events as fetch_f1
from fetchers.tennis import fetch_week_events as fetch_tennis
from generator import generate_html
from card_generator import generate_card_html
from relatos import get_relatos

MX_TZ = pytz.timezone(TIMEZONE)
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "docs", "index.html")
OUTPUT_PNG  = os.path.join(os.path.dirname(__file__), "docs", "agenda_koleos.png")


def main():
    generate_png = "--no-png" not in sys.argv

    print(f"\n{'='*50}")
    print(f"  Sports Agenda Generator — Koleos")
    print(f"  {datetime.now(MX_TZ).strftime('%d/%m/%Y %H:%M')} CDMX")
    print(f"{'='*50}\n")

    all_events = []

    # Fútbol + NBA via ESPN
    print("📡 Consultando ESPN (fútbol + NBA)...")
    try:
        espn_events = fetch_espn()
        futbol = [e for e in espn_events if e["sport"] == "Fútbol"]
        nba    = [e for e in espn_events if e["sport"] == "NBA"]
        print(f"  ✓ Fútbol: {len(futbol)} | NBA: {len(nba)}")
        all_events.extend(espn_events)
    except Exception as e:
        print(f"  ✗ Error ESPN: {e}")

    # F1
    if TRACK_F1:
        print("📡 Consultando F1...")
        try:
            f1 = fetch_f1()
            print(f"  ✓ F1: {len(f1)} sesiones")
            all_events.extend(f1)
        except Exception as e:
            print(f"  ✗ Error F1: {e}")

    # Tennis
    if TRACK_TENNIS:
        print("📡 Consultando tenis...")
        try:
            tennis = fetch_tennis()
            print(f"  ✓ Tenis: {len(tennis)}")
            all_events.extend(tennis)
        except Exception as e:
            print(f"  ✗ Error tenis: {e}")

    print(f"\n🎯 Total: {len(all_events)} eventos esta semana\n")

    # Relatos
    print("✍️  Generando relatos...")
    resumen, relatos_map = get_relatos(all_events)

    os.makedirs("docs", exist_ok=True)

    # HTML completo (GitHub Pages)
    print("\n🖥️  Generando HTML completo...")
    html = generate_html(all_events)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {OUTPUT_HTML}")

    # Card HTML + PNG
    print("🎨  Generando card visual...")
    card_html = generate_card_html(all_events, resumen, relatos_map)

    if generate_png:
        try:
            from screenshot import render_card
            png_path = render_card(card_html)
            print(f"  ✓ PNG: {png_path}")
            # Abrir automáticamente para preview
            os.system(f'open "{png_path}"')
        except Exception as e:
            print(f"  ✗ Error PNG: {e}")
            card_only = os.path.join("docs", "card.html")
            with open(card_only, "w", encoding="utf-8") as f:
                f.write(card_html)
            print(f"  → Card HTML guardado: {card_only}")
    else:
        card_only = os.path.join("docs", "card.html")
        with open(card_only, "w", encoding="utf-8") as f:
            f.write(card_html)
        print(f"  ✓ Card HTML: {card_only}")

    print(f"""
{'='*50}
  Archivos generados:
  📄 HTML:  docs/index.html
  🖼️  PNG:   docs/agenda_koleos.png

  Para publicar: python3 push.py
  Para relatos personalizados: python3 generate_prompt.py
{'='*50}
""")


if __name__ == "__main__":
    main()

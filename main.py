#!/usr/bin/env python3
"""
Sports Agenda — Koleos
Genera docs/index.html + docs/agenda_koleos.png
"""
import os, sys
from datetime import datetime
import pytz

from config import TIMEZONE, TRACK_F1, TRACK_RUGBY, TRACK_TENNIS, TRACK_NBA
from fetchers.espn import fetch_week as fetch_espn
from fetchers.f1 import fetch_week_events as fetch_f1
from fetchers.tennis import fetch_week_events as fetch_tennis
from fetchers.rugby import fetch_week_events as fetch_rugby
from relevance import filter_and_sort
from generator import generate_html
from card_generator import generate_card_html
from relatos import get_relatos

MX_TZ = pytz.timezone(TIMEZONE)
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "docs", "index.html")


def main():
    generate_png = "--no-png" not in sys.argv

    print(f"\n{'='*50}")
    print(f"  Sports Agenda Generator — Koleos")
    print(f"  {datetime.now(MX_TZ).strftime('%d/%m/%Y %H:%M')} CDMX")
    print(f"{'='*50}\n")

    raw_events = []

    print("📡 Consultando ESPN (fútbol + NBA)...")
    try:
        espn = fetch_espn()
        print(f"  ✓ {len(espn)} eventos crudos")
        raw_events.extend(espn)
    except Exception as e:
        print(f"  ✗ {e}")

    if TRACK_F1:
        print("📡 Consultando F1...")
        try:
            f1 = fetch_f1()
            print(f"  ✓ {len(f1)} sesiones")
            raw_events.extend(f1)
        except Exception as e:
            print(f"  ✗ {e}")

    if TRACK_RUGBY:
        print("📡 Consultando Rugby...")
        try:
            rugby = fetch_rugby()
            print(f"  ✓ {len(rugby)} eventos")
            raw_events.extend(rugby)
        except Exception as e:
            print(f"  ✗ {e}")

    if TRACK_TENNIS:
        print("📡 Consultando Tenis...")
        try:
            tennis = fetch_tennis()
            print(f"  ✓ {len(tennis)} eventos")
            raw_events.extend(tennis)
        except Exception as e:
            print(f"  ✗ {e}")

    # Filtrar y ordenar por relevancia
    events = filter_and_sort(raw_events)

    print(f"\n🎯 {len(raw_events)} eventos → {len(events)} relevantes tras filtro\n")
    if events:
        print("  Top 5:")
        for e in events[:5]:
            print(f"    [{e['score']:3d}] {e['sport']:10s} {e.get('home','')} vs {e.get('away','')} — {e['date']}")

    print("\n✍️  Generando relatos...")
    resumen, relatos_map = get_relatos(events)

    os.makedirs("docs", exist_ok=True)

    print("\n🖥️  HTML completo...")
    html = generate_html(events)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {OUTPUT_HTML}")

    print("🎨  Card visual...")
    card_html = generate_card_html(events, resumen, relatos_map)

    if generate_png:
        try:
            from screenshot import render_card
            png = render_card(card_html)
            print(f"  ✓ PNG: {png}")
            os.system(f'open "{png}"')
        except Exception as e:
            print(f"  ✗ PNG error: {e}")
            path = os.path.join("docs","card.html")
            with open(path,"w",encoding="utf-8") as f: f.write(card_html)
            print(f"  → Guardado como HTML: {path}")
    else:
        path = os.path.join("docs","card.html")
        with open(path,"w",encoding="utf-8") as f: f.write(card_html)
        print(f"  ✓ {path}")

    print(f"\n{'='*50}\n  python3 push.py  →  publica en GitHub Pages\n{'='*50}\n")


if __name__ == "__main__":
    main()

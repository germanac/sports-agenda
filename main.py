#!/usr/bin/env python3
"""
Sports Agenda — Koleos
Corre este script para generar docs/index.html con la agenda deportiva.
Luego hacé git push y se actualiza GitHub Pages automáticamente.
"""

import os
from datetime import datetime
import pytz

from config import TIMEZONE, TRACK_F1, TRACK_NBA, TRACK_TENNIS
from fetchers.espn import fetch_week as fetch_espn
from fetchers.f1 import fetch_week_events as fetch_f1
from fetchers.tennis import fetch_week_events as fetch_tennis
from generator import generate_html

MX_TZ = pytz.timezone(TIMEZONE)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "docs", "index.html")


def main():
    print(f"\n{'='*50}")
    print(f"  Sports Agenda Generator")
    print(f"  {datetime.now(MX_TZ).strftime('%d/%m/%Y %H:%M')} CDMX")
    print(f"{'='*50}\n")

    all_events = []

    # Fútbol + NBA via ESPN
    print("📡 Consultando ESPN (fútbol + NBA)...")
    try:
        espn_events = fetch_espn()
        futbol = [e for e in espn_events if e["sport"] == "Fútbol"]
        nba = [e for e in espn_events if e["sport"] == "NBA"]
        print(f"  ✓ Fútbol: {len(futbol)} partidos | NBA: {len(nba)} juegos")
        all_events.extend(espn_events)
    except Exception as e:
        print(f"  ✗ Error ESPN: {e}")

    # F1 via Jolpica
    if TRACK_F1:
        print("📡 Consultando F1 (Jolpica)...")
        try:
            f1 = fetch_f1()
            print(f"  ✓ F1: {len(f1)} sesiones")
            all_events.extend(f1)
        except Exception as e:
            print(f"  ✗ Error F1: {e}")

    # Tennis via TheSportsDB
    if TRACK_TENNIS:
        print("📡 Consultando tenis...")
        try:
            tennis = fetch_tennis()
            print(f"  ✓ Tenis: {len(tennis)} eventos")
            all_events.extend(tennis)
        except Exception as e:
            print(f"  ✗ Error tenis: {e}")

    print(f"\n🎯 Total: {len(all_events)} eventos esta semana")

    print("\n🖥️  Generando HTML...")
    html = generate_html(all_events)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✓ Guardado en: {OUTPUT_PATH}")
    print(f"""
{'='*50}
  Para publicar en GitHub Pages:

  git add docs/index.html
  git commit -m "Agenda {datetime.now(MX_TZ).strftime('%d/%m/%Y')}"
  git push

  O simplemente: python3 push.py
{'='*50}
""")


if __name__ == "__main__":
    main()

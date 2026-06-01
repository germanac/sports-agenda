#!/usr/bin/env python3
"""Genera la agenda y la pushea a GitHub Pages en un solo comando."""
import subprocess
import sys
from datetime import datetime
import pytz

# Primero generar
import main as agenda_main
agenda_main.main()

# Luego pushear
print("🚀 Pusheando a GitHub Pages...")
cmds = [
    ["git", "add", "docs/index.html"],
    ["git", "commit", "-m", f"Agenda {datetime.now(pytz.timezone('America/Mexico_City')).strftime('%d/%m/%Y %H:%M')}"],
    ["git", "push"],
]
for cmd in cmds:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Error: {result.stderr}")
        sys.exit(1)
    print(f"  ✓ {' '.join(cmd)}")

print("\n✅ Publicado! Tu agenda está live en GitHub Pages.")

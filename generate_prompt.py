#!/usr/bin/env python3
"""
Genera el prompt para pegar en Claude.ai y obtener los relatos.
Uso:
  1. python3 generate_prompt.py     → crea prompt_para_claude.txt
  2. Pegá el contenido en Claude.ai
  3. Copiá la respuesta JSON
  4. python3 generate_prompt.py --save   → te pide que pegues la respuesta
"""
import sys
from fetchers.espn import fetch_week as fetch_espn
from fetchers.f1 import fetch_week_events as fetch_f1
from relatos import generate_prompt_file, save_manual_response

def main():
    if "--save" in sys.argv:
        print("Pegá la respuesta JSON de Claude.ai (Ctrl+D cuando termines):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        save_manual_response("\n".join(lines))
        return

    print("Recolectando eventos de la semana...")
    events = fetch_espn() + fetch_f1()
    prompt_file = generate_prompt_file(events)
    print(f"\n✓ Prompt generado: {prompt_file}")
    print("\nPasos:")
    print("  1. Abrí prompt_para_claude.txt")
    print("  2. Copiá todo el contenido")
    print("  3. Pegalo en Claude.ai y mandalo")
    print("  4. Copiá la respuesta JSON completa")
    print("  5. Corrí: python3 generate_prompt.py --save")
    print("  6. Pegá el JSON y presioná Ctrl+D")
    print("  7. Corrí: python3 main.py   (ya usará los relatos guardados)")

if __name__ == "__main__":
    main()

"""
Toma screenshot del card HTML usando Playwright y lo guarda como PNG.
"""
import os
from playwright.sync_api import sync_playwright


CARD_HTML_PATH = os.path.join(os.path.dirname(__file__), "docs", "card.html")
OUTPUT_PNG = os.path.join(os.path.dirname(__file__), "docs", "agenda_koleos.png")


def render_card(html_content):
    """Guarda el HTML y captura el PNG."""
    os.makedirs(os.path.dirname(CARD_HTML_PATH), exist_ok=True)

    with open(CARD_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})

        # Cargar el HTML
        page.goto(f"file://{CARD_HTML_PATH}")

        # Esperar que carguen fuentes/imágenes
        page.wait_for_load_state("networkidle", timeout=10000)

        # Capturar el contenido completo (alto variable)
        body_height = page.evaluate("document.body.scrollHeight")
        page.set_viewport_size({"width": 390, "height": body_height})

        page.screenshot(path=OUTPUT_PNG, full_page=True)
        browser.close()

    return OUTPUT_PNG

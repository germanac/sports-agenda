"""
Captura el card HTML en exactamente 390×844px (iPhone 14) como PNG.
"""
import os
from playwright.sync_api import sync_playwright

CARD_HTML_PATH = os.path.join(os.path.dirname(__file__), "docs", "card.html")
OUTPUT_PNG     = os.path.join(os.path.dirname(__file__), "docs", "agenda_koleos.png")

# iPhone 14: 390×844pt lógicos, pixel ratio 3x → 1170×2532px real
IPHONE_W = 390
IPHONE_H = 844
PIXEL_RATIO = 3   # alta resolución para que se vea nítido en pantalla


def render_card(html_content):
    os.makedirs(os.path.dirname(CARD_HTML_PATH), exist_ok=True)

    with open(CARD_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": IPHONE_W, "height": IPHONE_H},
            device_scale_factor=PIXEL_RATIO,
        )
        page.goto(f"file://{os.path.abspath(CARD_HTML_PATH)}")
        page.wait_for_load_state("networkidle", timeout=10000)

        # Clip exacto: no full_page, solo el viewport
        page.screenshot(
            path=OUTPUT_PNG,
            clip={"x": 0, "y": 0, "width": IPHONE_W, "height": IPHONE_H},
        )
        browser.close()

    return OUTPUT_PNG

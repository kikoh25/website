"""Gera os PDFs em materiais/ a partir de tools/pdf/*.html (Playwright)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for src, out in [('checklist', 'checklist-automacao-nexus'), ('apresentacao', 'apresentacao-nexus-ef-business')]:
        pg.goto((R / 'tools/pdf' / f'{src}.html').as_uri())
        pg.pdf(path=str(R / 'materiais' / f'{out}.pdf'), format='A4', print_background=True, margin=dict(top='0', bottom='0', left='0', right='0'))
    b.close()

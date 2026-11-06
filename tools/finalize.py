"""Padroniza URLs para o formato servido pelo Cloudflare (sem .html; index vira pasta).
Idempotente. Roda ao final do build sobre todos os .html, sitemap, feed e scripts do site."""
import re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
PAT = re.compile(r'(?<=["\'(])((?:https://(?:www\.)?nexusefbusiness\.com\.br)?)/([A-Za-z0-9/_-]*?)(index)?\.html(?=["\'#?)<])')
def fix(m):
    host, path, idx = m.group(1), m.group(2), m.group(3)
    if idx is not None:
        return f'{host}/{path}'          # /blog/index.html -> /blog/ ; /index.html -> /
    return f'{host}/{path}'
files = [p for p in R.rglob('*') if p.suffix in ('.html', '.js', '.xml', '.webmanifest') and not any(x in p.parts for x in ('tools', 'node_modules', '.git', '.wrangler'))]
n = 0
for p in files:
    s = p.read_text(encoding='utf-8'); t = PAT.sub(fix, s)
    if p.name == 'sw.js':
        t = t.replace("'/offline.html'", "'/offline'")
    if t != s:
        p.write_text(t, encoding='utf-8'); n += 1
print('finalize ok:', n, 'arquivos ajustados')

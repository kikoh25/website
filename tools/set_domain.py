"""Troca o domínio principal em canonical, og:url, sitemap, robots, hreflang e JSON-LD.
Uso (simulação): python3 tools/set_domain.py https://www.nexusefbusiness.com.br
Para aplicar:    python3 tools/set_domain.py https://www.nexusefbusiness.com.br --apply
Antes de aplicar: o domínio novo precisa estar ligado ao Worker no Cloudflare e o antigo deve redirecionar 301 para ele."""
import sys, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
new = sys.argv[1].rstrip('/'); apply = '--apply' in sys.argv
old_pat = re.compile(r'https://(?:www\.)?nexusefbusiness\.com\.br')
n = 0
for p in R.rglob('*'):
    if p.suffix not in ('.html', '.xml', '.txt', '.webmanifest', '.py') or any(x in p.parts for x in ('node_modules', '.git', '.wrangler')):
        continue
    if p.suffix == '.py' and p.name not in ('lib.py', 'migrate_legacy.py'):
        continue
    s = p.read_text(encoding='utf-8'); t = old_pat.sub(new, s)
    if t != s:
        n += len(old_pat.findall(s))
        if apply: p.write_text(t, encoding='utf-8')
print(('aplicado' if apply else 'simulação') + f': {n} ocorrências para {new}')

"""Funções compartilhadas pelos geradores de páginas do site.

O cabeçalho (head), o menu e o rodapé são lidos de index.html, que é a
fonte única. Para mudar o menu ou o rodapé de todas as páginas geradas,
altere index.html (ou migrate_legacy.py) e rode `python3 tools/build.py`.
"""
import re, json, os, math, html as _html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://nexusefbusiness.com.br'
PHONE = '5511926461357'
WA = 'https://wa.me/5511926461357?text='  # compatibilidade com textos antigos


def rd(f):
    return (ROOT / f).read_text(encoding='utf-8')


def wr(f, s):
    p = ROOT / f
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')


def wa(msg):
    return f'https://wa.me/{PHONE}?text=' + quote(msg, safe='')


def esc(s):
    return _html.escape(s, quote=True)


_idx = rd('index.html')
HEAD0 = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', _idx[:_idx.index('<body')], flags=re.S)
_ns = _idx.index('<nav>')
NAV = _idx[_ns:_idx.index('</nav>') + 6]
_fi = _idx.index('<footer>')
FOOTER = _idx[_fi:_idx.index('</footer>') + 9]
for _a in ['sobre', 'servicos', 'diferenciais', 'produtos', 'contato', 'faq', 'numeros', 'processo', 'publico', 'tecnologias', 'ferramentas']:
    NAV = NAV.replace(f'href="#{_a}"', f'href="/#{_a}"')
    FOOTER = FOOTER.replace(f'href="#{_a}"', f'href="/#{_a}"')
NAV = NAV.replace('href="#" class="nav-logo"', 'href="/" class="nav-logo"')
FOOTER = FOOTER.replace('href="#"', 'href="/"')
WA_SVG = re.search(r'<svg viewBox="0 0 32 32".*?</svg>', _idx, re.S).group(0)


def fab(txt='Olá! Vim pelo site da Nexus EF Business.', label='Falar no WhatsApp'):
    return (f'<a href="{wa(txt)}" target="_blank" rel="noopener" aria-label="{label}" '
            f'class="wa-float">{WA_SVG}</a>')


def crumbs_html(crumbs):
    if not crumbs:
        return ''
    out = []
    for i, (name, url) in enumerate(crumbs):
        if url and i < len(crumbs) - 1:
            out.append(f'<li><a href="{url}">{name}</a></li>')
        else:
            out.append(f'<li aria-current="page">{name}</li>')
    return '<div class="crumbs" role="navigation" aria-label="Caminho"><ol>' + ''.join(out) + '</ol></div>'


def crumbs_ld(crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs, 1):
        it = {"@type": "ListItem", "position": i, "name": re.sub(r'<[^>]+>', '', name)}
        if url:
            it["item"] = SITE + url
        items.append(it)
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}, ensure_ascii=False)


def HERO(eb, h1, sub, crumbs=None, meta=''):
    return f'''<section class="page-hero">
  <div class="section-inner" style="max-width:860px">
    {crumbs_html(crumbs)}
    <p class="section-eyebrow" style="color:#C4B5FD">{eb}</p>
    <h1>{h1}</h1>
    <p class="page-hero-sub">{sub}</p>
    {('<p class="page-hero-meta">' + meta + '</p>') if meta else ''}
  </div>
</section>'''


def CTA(msg, title='Quer aplicar isso na sua empresa?', text='Conte o seu cenário e a gente analisa com você, sem compromisso.', btn='Falar no WhatsApp', alt_label='Apresentar meu projeto'):
    return f'''<div class="cta-box">
  <strong>{title}</strong>
  <p>{text}</p>
  <a href="{wa(msg)}" target="_blank" rel="noopener" class="btn-primary">{btn}</a>
  <a href="/projeto.html" style="display:inline-block;margin:.6rem 0 0 .8rem;color:#fff;font-weight:600;text-decoration:underline">{alt_label}</a>
</div>'''


def slugify(t):
    t = re.sub(r'<[^>]+>', '', t).lower()
    for a, b in zip('áàâãäéèêëíìîïóòôõöúùûüç', 'aaaaaeeeeiiiiooooouuuuc'):
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def article_prep(body):
    """Adiciona ids nos h2, gera índice e tempo de leitura."""
    heads = re.findall(r'<h2>(.*?)</h2>', body)
    for h in heads:
        body = body.replace(f'<h2>{h}</h2>', f'<h2 id="{slugify(h)}">{h}</h2>', 1)
    toc = ''
    if len(heads) >= 3:
        toc = ('<aside class="toc" aria-label="Neste artigo"><p>Neste artigo</p><ul>'
               + ''.join(f'<li><a href="#{slugify(h)}">{re.sub(r"<[^>]+>", "", h)}</a></li>' for h in heads)
               + '</ul></aside>')
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    return body, toc, max(1, math.ceil(words / 190))


def page(path, title, desc, main, extra_head='', crumbs=None, exit_popup=False, lang='pt-BR',
         alt=None, img=None, nav=None, footer=None, body_attrs='', og_type='website'):
    url = SITE + '/' + path
    h = HEAD0
    h = re.sub(r'<title>.*?</title>', lambda m: f'<title>{title}</title>', h, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, h)
    h = h.replace('<meta property="og:type" content="website" />', f'<meta property="og:type" content="{og_type}" />')
    if img:
        h = re.sub(r'(<meta property="og:image" content=")[^"]*', lambda m: m.group(1) + img, h)
    if lang != 'pt-BR':
        h = h.replace('<html lang="pt-BR">', f'<html lang="{lang}">')
        h = h.replace('<meta property="og:locale" content="pt_BR" />', '<meta property="og:locale" content="en_US" />')
    # hreflang do index não deve ser herdado
    h = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', '', h)
    extra = extra_head
    if alt:
        extra += ''.join(f'<link rel="alternate" hreflang="{k}" href="{SITE}{v}" />\n' for k, v in alt.items())
    if crumbs:
        extra += f'<script type="application/ld+json">{crumbs_ld(crumbs)}</script>\n'
    h = h.replace('</head>', extra + '</head>')
    attrs = (' data-exit="1"' if exit_popup else '') + (' ' + body_attrs if body_attrs else '')
    skip = 'Pular para o conteúdo' if lang.startswith('pt') else 'Skip to content'
    return (h + f'<body{attrs}>\n<a href="#conteudo" class="skip-link">{skip}</a>\n' + (nav or NAV)
            + '\n<main id="conteudo">\n' + main + '\n</main>\n' + (footer or FOOTER) + '\n' + (fab() if lang.startswith('pt') else fab('Hello! I came from the English page of the Nexus EF Business website.', 'Chat on WhatsApp'))
            + '\n<script src="/assets/site.js" defer></script>\n</body>\n</html>\n')

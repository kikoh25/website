"""Gera as páginas do site. Uso: cd tools && python3 migrate_legacy.py && python3 build.py

Ordem: 1) migrate_legacy.py atualiza index e páginas originais;
2) build.py gera blog, ferramentas, públicos, sobre, status, inglês, feed e sitemap.
"""
import sys, time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from lib import *
from posts import posts, TAGS, DATE

ORDER_DATE_RFC = 'Wed, 04 Nov 2026 12:00:00 -0300'

# ---------- diagnóstico e demo do Platform ----------
exec(open(ROOT / 'tools' / 'build_legacy_part.py', encoding='utf-8').read())

# ---------- blog ----------
FEAT = [
    ('/casos/sistema-contabil-34-modulos.html', 'Casos e guias', 'Estudo de caso: sistema contábil com 34 módulos',
     'Como o Nexus Contábil reúne fiscal, notas, contratos e atendimento em um só ambiente.'),
    ('/perguntas-sobre-automacao.html', 'Casos e guias', 'Perguntas sobre automação de processos',
     'Respostas curtas sobre custo, prazo, segurança e como começar.'),
]
cards = ''.join(
    f'<a class="post-card" href="{u}" data-tags="{tg}" data-title="{esc(t)}"><span class="post-tag">{tg}</span><h2>{t}</h2><p>{d}</p></a>\n'
    for u, tg, t, d in FEAT)
for slug, t, d, body, msg in posts:
    tag = TAGS[slug]
    cards += f'<a class="post-card" href="/blog/{slug}.html" data-tags="{tag}" data-title="{esc(t)}"><span class="post-tag">{tag}</span><h2>{t}</h2><p>{d}</p></a>\n'
    body, toc, mins = article_prep(body)
    rel = [p for p in posts if p[0] != slug and TAGS[p[0]] == tag][:2]
    rel += [p for p in posts if p[0] != slug and p not in rel][:max(0, 2 - len(rel))]
    related = ''.join(f'<a class="post-card" href="/blog/{p[0]}.html"><span class="post-tag">{TAGS[p[0]]}</span><h3>{p[1]}</h3><p>{p[2]}</p></a>' for p in rel)
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": t, "description": d,
                     "datePublished": DATE, "dateModified": DATE, "inLanguage": "pt-BR",
                     "image": SITE + "/img/og.jpg",
                     "author": {"@type": "Organization", "name": "Nexus EF Business"},
                     "publisher": {"@type": "Organization", "name": "Nexus EF Business",
                                   "logo": {"@type": "ImageObject", "url": SITE + "/img/logo.png"}},
                     "mainEntityOfPage": f"{SITE}/blog/{slug}.html"}, ensure_ascii=False)
    url = f'{SITE}/blog/{slug}.html'
    share = (f'<div class="share-row"><button type="button" data-copy>Copiar link</button>'
             f'<a href="https://wa.me/?text={quote(t + " " + url, safe="")}" target="_blank" rel="noopener">Compartilhar no WhatsApp</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url, safe="")}" target="_blank" rel="noopener">LinkedIn</a></div>')
    main = HERO(f'Blog · {tag}', t, d, crumbs=[('Início', '/'), ('Blog', '/blog/'), (t, None)],
                meta=f'{mins} min de leitura · 4 de novembro de 2026') + f'''
<article class="sec-white" style="padding:3rem 5% 5rem"><div class="section-inner article" style="max-width:760px">
{toc}
{body}
{CTA(msg)}
{share}
<h2 style="margin-top:2.6rem">Continue lendo</h2>
<div class="card-grid" style="margin-top:1rem">{related}</div>
<p style="margin-top:2rem"><a href="/blog/">Voltar para o blog</a></p>
</div></article>'''
    wr(f'blog/{slug}.html', page(f'blog/{slug}.html', (t if len(t) + 20 > 65 else f'{t} | Nexus EF Business'), d, main,
                                  f'<script type="application/ld+json">{ld}</script>\n',
                                  crumbs=[('Início', '/'), ('Blog', '/blog/'), (t, None)], exit_popup=True, og_type='article'))

tagnames = ['Automação', 'Integração', 'TI e helpdesk', 'Gestão', 'Casos e guias']
chips = '<button type="button" class="tag-btn" data-tag="all" aria-pressed="true">Todos</button>' + ''.join(
    f'<button type="button" class="tag-btn" data-tag="{t}" aria-pressed="false">{t}</button>' for t in tagnames)
idxmain = HERO('Blog', 'Automação, integração e TI na prática',
               'Artigos curtos para decidir melhor o que automatizar, integrar e organizar na sua empresa.',
               crumbs=[('Início', '/'), ('Blog', None)]) + f'''
<section class="sec-lav" style="padding:3rem 5% 5rem"><div class="section-inner" data-blog>
  <div class="blog-tools">
    <label for="blogSearch" class="sr-only" style="position:absolute;left:-9999px">Buscar artigos</label>
    <input type="search" id="blogSearch" placeholder="Buscar artigos" autocomplete="off" />
    <span id="blogCount" role="status" aria-live="polite" style="font-size:.85rem;color:var(--gray-600)"></span>
  </div>
  <div class="blog-tools" style="margin-top:1rem" role="group" aria-label="Filtrar por tema">{chips}</div>
  <div class="post-grid">
{cards}  </div>
  <p id="noResults" class="no-results" role="status">Nenhum artigo encontrado. Tente outro termo ou limpe o filtro.</p>
</div></section>'''
wr('blog/index.html', page('blog/', 'Blog | Nexus EF Business',
                            'Artigos sobre automação de processos, integração de sistemas, helpdesk e controle de ativos de TI.',
                            idxmain, crumbs=[('Início', '/'), ('Blog', None)], exit_popup=True))

# ---------- casos e perguntas ----------
exec(open(ROOT / 'tools' / 'pages_extra.py', encoding='utf-8').read())

# ---------- páginas novas ----------
exec(open(ROOT / 'tools' / 'pages_new.py', encoding='utf-8').read())

exec(open(ROOT / 'tools' / 'pages_solucoes.py', encoding='utf-8').read())
exec(open(ROOT / 'tools' / 'pages_projeto.py', encoding='utf-8').read())
exec(open(ROOT / 'tools' / 'pages_servicos.py', encoding='utf-8').read())
exec(open(ROOT / 'tools' / 'pages_en.py', encoding='utf-8').read())

# ---------- feed RSS ----------
items = ''.join(f'''  <item>
    <title>{esc(t)}</title>
    <link>{SITE}/blog/{slug}.html</link>
    <guid isPermaLink="true">{SITE}/blog/{slug}.html</guid>
    <pubDate>{ORDER_DATE_RFC}</pubDate>
    <category>{esc(TAGS[slug])}</category>
    <description>{esc(d)}</description>
  </item>
''' for slug, t, d, body, msg in posts)
wr('feed.xml', f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Blog Nexus EF Business</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml" />
  <description>Automação, integração e TI na prática.</description>
  <language>pt-BR</language>
  <lastBuildDate>{ORDER_DATE_RFC}</lastBuildDate>
{items}</channel>
</rss>
''')

# ---------- sitemap (automático) ----------
skip = {'404.html', 'offline.html'}
urls = []
for p in sorted(ROOT.rglob('*.html')):
    rel = p.relative_to(ROOT).as_posix()
    if rel in skip or rel.startswith(('tools/', 'assets/', 'node_modules/')):
        continue
    u = rel[:-len('index.html')] if rel.endswith('index.html') else rel
    urls.append(u)
urls.sort(key=lambda u: (u != '', u))
today = time.strftime('%Y-%m-%d')
wr('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
   + ''.join(f'  <url><loc>{SITE}/{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
print('build ok:', len(urls), 'urls')

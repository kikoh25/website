"""Atualiza, de forma idempotente, as páginas originais (index, servicos, privacidade,
404, nexus-platform, nexus-contabil) com os recursos compartilhados.
Pode ser rodado várias vezes sem duplicar nada."""
import re
from lib import rd, wr, wa

THEME_INIT = ("<script>(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia"
              "('(prefers-color-scheme: dark)').matches))document.documentElement.setAttribute('data-theme','dark')}"
              "catch(e){}})();</script>\n")
HEAD_LINKS = ('<link rel="stylesheet" href="/assets/site.css" />\n'
              '<link rel="manifest" href="/manifest.webmanifest" />\n'
              '<link rel="apple-touch-icon" href="/img/icon-192.png" />\n'
              '<link rel="alternate" type="application/rss+xml" title="Blog Nexus EF Business" href="/feed.xml" />\n')
OLD_NAV_JS = rd('tools/navjs.html')
NEW_JS = '<script src="/assets/site.js" defer></script>\n</body>'

SUN = '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
TOOLS_LI = (f'    <li class="nav-tools"><button type="button" class="theme-toggle" aria-label="Mudar para tema escuro" aria-pressed="false">{MOON}{SUN}</button>'
            '<a class="lang-link" href="/en/" hreflang="en" lang="en" aria-label="English version">EN</a></li>\n')

THEME_PAGES = ['index.html', 'servicos.html', 'privacidade.html', '404.html']
ALL_PAGES = THEME_PAGES + ['nexus-platform.html', 'nexus-contabil.html']

for f in ALL_PAGES:
    s = rd(f)
    # 1) head
    if '/assets/site.css' not in s:
        pre = THEME_INIT if f in THEME_PAGES else ''
        s = s.replace('</head>', pre + HEAD_LINKS + '</head>', 1)
    # 2) script do menu antigo -> site.js
    if OLD_NAV_JS in s:
        s = s.replace(OLD_NAV_JS, NEW_JS, 1)
    elif 'assets/site.js' not in s:
        s = s.replace('</body>', NEW_JS, 1)
    if f in THEME_PAGES:
        # 3) itens do menu
        if '/ferramentas/' not in s.split('</nav>')[0]:
            s = re.sub(r'(<li><a href="/blog/">Blog</a></li>)', r'\1\n    <li><a href="/ferramentas/">Ferramentas</a></li>', s, count=1)
        if 'nav-tools' not in s.split('</nav>')[0]:
            s = re.sub(r'(\n    <li><a href="[^"]*#contato" class="nav-cta">)', '\n' + TOOLS_LI.rstrip('\n') + r'\1', s, count=1)
        # 4) rodapé
        if '/sobre.html' not in s.split('<footer')[1]:
            s = s.replace('<li><a href="/privacidade.html">Privacidade</a></li>',
                          '<li><a href="/sobre.html">Sobre</a></li>\n    <li><a href="/ferramentas/">Ferramentas</a></li>\n'
                          '    <li><a href="/status.html">Status</a></li>\n    <li><a href="/en/" hreflang="en" lang="en">English</a></li>\n'
                          '    <li><a href="/privacidade.html">Privacidade</a></li>', 1)
    # popup de saída
    if f in ('index.html', 'servicos.html') and 'data-exit' not in s:
        s = s.replace('<body>', '<body data-exit="1">', 1)
    wr(f, s)

# ---------- Seções novas da home ----------
s = rd('index.html')

NUMEROS = '''<!-- NUMEROS -->
<section id="numeros" class="stats-strip" aria-label="A Nexus em números">
  <div class="stats-grid">
    <div><div class="stat-n"><span data-count="40" data-suffix="+">40+</span></div><p class="stat-l">telas de gestão no Nexus Contábil</p></div>
    <div><div class="stat-n"><span data-count="5">5</span></div><p class="stat-l">ferramentas gratuitas para medir o custo dos processos manuais</p></div>
    <div><div class="stat-n"><span data-count="6">6</span></div><p class="stat-l">empresas com TI estruturada em um mesmo grupo</p></div>
    <div><div class="stat-n"><span data-count="2">2</span></div><p class="stat-l">produtos próprios em nova versão, com acesso antecipado</p></div>
  </div>
</section>

'''

PUBLICO = '''<!-- PUBLICO -->
<section id="publico" style="background:var(--white)">
  <div class="section-inner">
    <p class="section-eyebrow reveal">Para quem é</p>
    <h2 class="section-title reveal">Soluções pensadas para o seu tipo de operação</h2>
    <p class="section-sub reveal">Cada setor tem as suas dores. Veja como a Nexus ajuda no seu caso.</p>
    <div class="card-grid">
      <a class="aud-card reveal" href="/solucoes/contabilidade.html"><div class="ico" aria-hidden="true">📊</div><h3>Escritórios contábeis</h3><p>Sistema completo com SEFAZ, NFS-e e apuração, mais automações para o dia a dia da carteira.</p><span class="go">Ver como ajudamos →</span></a>
      <a class="aud-card reveal" href="/para/empresas-de-eventos.html"><div class="ico" aria-hidden="true">🎤</div><h3>Empresas de eventos</h3><p>Captura de leads e automação antes, durante e depois do evento, com voz e IA em desenvolvimento.</p><span class="go">Ver como ajudamos →</span></a>
      <a class="aud-card reveal" href="/para/times-de-ti.html"><div class="ico" aria-hidden="true">🖥️</div><h3>Times de TI</h3><p>Helpdesk com SLA, inventário de ativos e integração com Slack, Teams e n8n.</p><span class="go">Ver como ajudamos →</span></a>
    </div>
  </div>
</section>

'''

chips = ['NestJS', 'Next.js', 'TypeScript', 'Node.js', 'Python', 'PostgreSQL', 'Prisma', 'Docker', 'Nginx', 'Cloudflare', 'n8n', 'Slack API', 'GitHub', 'Linux']
row = ''.join(f'<span class="chip">{c}</span>' for c in chips)
TECNO = f'''<!-- TECNOLOGIAS -->
<section id="tecnologias" style="background:var(--white)">
  <div class="section-inner">
    <p class="section-eyebrow reveal">Tecnologias</p>
    <h2 class="section-title reveal">Ferramentas modernas, escolhidas para durar</h2>
    <p class="section-sub reveal">Usamos tecnologias consolidadas, com boa documentação e comunidade, para o seu sistema ser fácil de manter e evoluir.</p>
    <div class="marquee" aria-label="Tecnologias que usamos"><div class="marquee-track">{row}<span aria-hidden="true" style="display:contents">{row}</span></div></div>
  </div>
</section>

'''

FERR = '''<!-- FERRAMENTAS -->
<section id="ferramentas" style="background:#F5F4FF">
  <div class="section-inner">
    <p class="section-eyebrow reveal">Ferramentas grátis</p>
    <h2 class="section-title reveal">Faça as contas antes de decidir</h2>
    <p class="section-sub reveal">Calculadoras e guias rápidos para você enxergar o custo dos processos manuais e escolher a melhor solução.</p>
    <div class="card-grid">
      <a class="tool-card reveal" href="/diagnostico.html"><div class="ico" aria-hidden="true">⏱️</div><h3>Diagnóstico de automação</h3><p>Estime as horas e o custo das tarefas repetitivas do seu time.</p><span class="go">Abrir →</span></a>
      <a class="tool-card reveal" href="/ferramentas/custo-chamado-ti.html"><div class="ico" aria-hidden="true">🎫</div><h3>Custo de um chamado de TI</h3><p>Descubra quanto custa cada atendimento e quanto dá para economizar.</p><span class="go">Abrir →</span></a>
      <a class="tool-card reveal" href="/ferramentas/custo-retrabalho.html"><div class="ico" aria-hidden="true">🔁</div><h3>Custo do retrabalho</h3><p>Calcule quanto os erros de digitação e conferência custam por mês.</p><span class="go">Abrir →</span></a>
      <a class="tool-card reveal" href="/ferramentas/comparador-solucao.html"><div class="ico" aria-hidden="true">⚖️</div><h3>Planilha, ERP ou sob medida?</h3><p>Responda 6 perguntas e veja qual caminho combina com a sua empresa.</p><span class="go">Abrir →</span></a>
      <a class="tool-card reveal" href="/checklist-automacao.html"><div class="ico" aria-hidden="true">✅</div><h3>Checklist de automação</h3><p>10 sinais de que a sua empresa precisa automatizar. Marque online ou baixe em PDF.</p><span class="go">Abrir →</span></a>
    </div>
  </div>
</section>

'''

for marker, block, key in [('<!-- SERVICOS -->', NUMEROS, 'id="numeros"'), ('<!-- DIFERENCIAIS -->', PUBLICO, 'id="publico"'),
                           ('<!-- PRODUTOS -->', TECNO, 'id="tecnologias"'), ('<!-- FAQ -->', FERR, 'id="ferramentas"')]:
    if key not in s:
        assert s.count(marker) == 1, marker
        s = s.replace(marker, block + marker, 1)

# link para a página sobre
if '/sobre.html" class="inline-link"' not in s:
    a = 'sem intermediários.</p>'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n        <p style="margin-top:.8rem"><a href="/sobre.html" class="inline-link" style="color:var(--purple);font-weight:600;text-decoration:none;font-size:.88rem">Conheça a trajetória do fundador →</a></p>', 1)

# hreflang
if 'hreflang="en"' not in s.split('</head>')[0]:
    s = s.replace('</head>', '<link rel="alternate" hreflang="pt-BR" href="https://nexusefbusiness.com.br/" />\n'
                  '<link rel="alternate" hreflang="en" href="https://nexusefbusiness.com.br/en/" />\n'
                  '<link rel="alternate" hreflang="x-default" href="https://nexusefbusiness.com.br/" />\n</head>', 1)
wr('index.html', s)
print('migrate ok')

# ---------- dados estruturados extras (sem preço, avaliação ou disponibilidade) ----------
import json
def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>\n'
SITE_ = 'https://nexusefbusiness.com.br'
EXTRA = {
 'index.html': ('"WebSite"', ld({"@context": "https://schema.org", "@type": "WebSite", "name": "Nexus EF Business", "url": SITE_ + "/", "inLanguage": "pt-BR"})),
 'nexus-contabil.html': ('"SoftwareApplication"', ld({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Nexus Contábil",
    "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "url": SITE_ + "/nexus-contabil",
    "description": "Sistema de gestão para escritórios de contabilidade, em nova versão com acesso antecipado.",
    "publisher": {"@type": "Organization", "name": "Nexus EF Business", "url": SITE_}}) +
    ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE_ + "/"}, {"@type": "ListItem", "position": 2, "name": "Nexus Contábil"}]})),
 'nexus-platform.html': ('"SoftwareApplication"', ld({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Nexus Platform",
    "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "url": SITE_ + "/nexus-platform",
    "description": "Plataforma de helpdesk e inventário de ativos de TI, em nova versão com acesso antecipado.",
    "publisher": {"@type": "Organization", "name": "Nexus EF Business", "url": SITE_}}) +
    ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE_ + "/"}, {"@type": "ListItem", "position": 2, "name": "Nexus Platform"}]})),
}
for f, (key, block) in EXTRA.items():
    s = rd(f)
    if key not in s:
        s = s.replace('</head>', block + '</head>', 1); wr(f, s)
print('ld extra ok')

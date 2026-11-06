# Versão em inglês (home resumida) com menu e rodapé próprios.
EN_NAV = NAV
for a, b in [('Sobre', 'About'), ('Serviços', 'Services'), ('Por que a Nexus', 'Why Nexus'), ('Produtos', 'Products'), ('Ferramentas', 'Tools'),
             ('Fale conosco', 'Contact us'), ('Abrir menu', 'Open menu'), ('Mudar para tema escuro', 'Switch to dark theme'), ('English version', 'Portuguese version')]:
    EN_NAV = EN_NAV.replace(f'>{a}<', f'>{b}<').replace(f'"{a}"', f'"{b}"')
EN_NAV = EN_NAV.replace('href="/#sobre"', 'href="#about"').replace('href="/servicos.html"', 'href="#services"').replace('href="/#diferenciais"', 'href="#why"')
EN_NAV = EN_NAV.replace('>Blog<', '>Blog (PT)<').replace('>Tools<', '>Tools (PT)<')
EN_NAV = EN_NAV.replace('href="/#produtos"', 'href="#products"').replace('href="/#contato"', 'href="#contact"').replace('href="/blog/"', 'href="/blog/" hreflang="pt-BR"')
EN_NAV = EN_NAV.replace('href="/ferramentas/"', 'href="/ferramentas/" hreflang="pt-BR"').replace('<a href="/" class="nav-logo">', '<a href="/en/" class="nav-logo">')
EN_NAV = EN_NAV.replace('href="/en/" hreflang="en" lang="en"', 'href="/" hreflang="pt-BR" lang="pt-BR"').replace('>EN<', '>PT<')
EN_FOOT = re.sub(r'<ul class="footer-links">.*?</ul>', '<ul class="footer-links"><li><a href="#services">Services</a></li><li><a href="#products">Products</a></li><li><a href="#contact">Contact</a></li><li><a href="/">Português</a></li><li><a href="/privacidade.html" hreflang="pt-BR">Privacy (PT)</a></li><li><a href="https://www.instagram.com/nexusefbusiness" target="_blank" rel="noopener">Instagram</a></li></ul>', FOOTER, flags=re.S)
EN_FOOT = EN_FOOT.replace('Soluções · Integrações · Automação', 'Solutions · Integrations · Automation').replace('Todos os direitos reservados.', 'All rights reserved.')
SV = [('🔌', 'System integration', 'Connect your ERP, CRM, spreadsheets and chat tools so data is entered once and flows everywhere.'),
      ('⚙️', 'Process automation', 'Replace repetitive manual work with reliable workflows, with approvals and audit trail.'),
      ('🧩', 'Custom software', 'Internal systems and dashboards built around how your company really works.'),
      ('🖥️', 'IT and helpdesk', 'Ticketing with SLA, asset inventory and reports for IT teams.')]
sv = ''.join(f'<div class="tool-card"><div class="ico" aria-hidden="true">{i}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in SV)
msg = 'Hello! I came from the English page of the Nexus EF Business website.'
main = f'''<section class="page-hero"><div class="section-inner" style="max-width:860px">
<p class="section-eyebrow" style="color:#C4B5FD">B2B technology, built to order</p>
<h1>We connect systems. We automate what matters.</h1>
<p class="page-hero-sub">Custom software, integrations and process automation for companies in Brazil. Direct contact with the developer, no middlemen.</p>
<p style="margin-top:1.5rem"><a href="{wa(msg)}" target="_blank" rel="noopener" class="btn-primary">Talk to us on WhatsApp</a></p></div></section>
<section id="about" class="sec-white" style="padding:3.5rem 5%"><div class="section-inner" style="max-width:860px"><h2 class="section-title">Who we are</h2>
<p style="line-height:1.9;color:var(--gray-600);margin-top:1rem">Nexus EF Business is a technology company founded by a full-stack developer with a background in IT infrastructure, financial systems and SaaS products. We build what your business needs, and we tell you plainly what is ready and what is still in development.</p></div></section>
<section id="services" class="sec-lav" style="padding:3.5rem 5%"><div class="section-inner"><h2 class="section-title">Services</h2><div class="card-grid" style="margin-top:1.5rem">{sv}</div></div></section>
<section id="why" class="sec-white" style="padding:3.5rem 5%"><div class="section-inner"><h2 class="section-title">Why Nexus</h2><div class="two-col" style="margin-top:1.5rem">
<div class="callout"><b>Honest delivery</b><p>We promise only what the product does today.</p></div>
<div class="callout"><b>Direct conversation</b><p>You talk to the person who builds your system.</p></div>
<div class="callout"><b>Built to last</b><p>Proven technology that is easy to maintain and evolve.</p></div></div></div></section>
<section id="products" class="sec-lav" style="padding:3.5rem 5%"><div class="section-inner"><h2 class="section-title">Our products</h2><div class="two-col" style="margin-top:1.5rem">
<div class="callout"><b>Nexus Contábil</b><p>Management platform for accounting firms: over 40 management screens and SEFAZ queries. New version with early access.</p><p style="margin-top:.6rem"><a href="/nexus-contabil.html" hreflang="pt-BR">See details (Portuguese)</a></p></div>
<div class="callout"><b>Nexus Platform</b><p>Helpdesk and IT asset inventory with SLA, CSAT and integrations. New version with early access.</p><p style="margin-top:.6rem"><a href="/nexus-platform.html" hreflang="pt-BR">See details (Portuguese)</a></p></div></div>
<p style="margin-top:1rem;font-size:.88rem;color:var(--gray-600)">Product pages are currently in Portuguese.</p></div></section>
<section id="contact" class="sec-white" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:760px">{CTA(msg, 'Let us talk about your project', 'Tell us about your scenario and we will review it with you, no strings attached.', 'Talk to us on WhatsApp', 'Present your project (in Portuguese)')}
<p style="margin-top:1rem;text-align:center;font-size:.9rem;color:var(--gray-600)">Email: <a href="mailto:contato@nexusefbusiness.com.br">contato@nexusefbusiness.com.br</a></p></div></section>'''
wr('en/index.html', page('en/', 'Nexus EF Business | Custom software, integrations and automation',
   'Custom software, system integrations and process automation for companies in Brazil. Direct contact with the developer.', main,
   lang='en', alt={'pt-BR': '/', 'en': '/en/', 'x-default': '/'}, nav=EN_NAV, footer=EN_FOOT))

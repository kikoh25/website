# Página de serviços (gerada). Sob demanda x produtos próprios. Exemplos reais só dos projetos do fundador.
SV10 = [
 ('sistemas', '🧩', 'Sistemas personalizados', 'Planilhas e ferramentas genéricas que não acompanham o jeito da sua empresa.',
  'Mapeamos o seu processo, desenhamos as telas e regras com você e entregamos em etapas que você valida. O sistema é feito para o seu fluxo, não o contrário.',
  'Controle de pedidos, cadastro de clientes, aprovações internas, rotinas financeiras.', 'Menos adaptação, menos retrabalho e dados em um lugar só.',
  'Entregue: sistema de gestão contábil (Nexus Contábil, em nova versão) e ERP financeiro com bots no Slack.', 'Olá! Quero conversar sobre um sistema personalizado para a minha empresa.'),
 ('saas', '☁️', 'Plataformas SaaS', 'Uma ideia de produto que precisa virar um serviço com login, planos e vários clientes.',
  'Estruturamos a base multiusuário, o controle de acesso e a cobrança recorrente, começando por uma primeira versão enxuta para validar com clientes reais.',
  'Sistema por assinatura para um nicho, portal de clientes, plataforma de gestão setorial.', 'Lançar mais rápido e crescer sem refazer a base.',
  'Entregue: Nexus Platform (helpdesk e inventário) e Nexus Contábil, ambos em nova versão com acesso antecipado.', 'Olá! Tenho uma ideia de plataforma SaaS e quero conversar.'),
 ('sites', '🌐', 'Sites profissionais', 'Site antigo, lento ou que não gera contato.',
  'Criamos páginas rápidas, que carregam bem no celular, com textos claros e botões de contato em pontos estratégicos. Cuidamos de domínio, hospedagem e SEO básico.',
  'Site institucional, página de produto, blog, páginas por segmento.', 'Mais credibilidade e mais pessoas entrando em contato.',
  'Este site é um exemplo: rápido, acessível e com ferramentas gratuitas.', 'Olá! Quero conversar sobre um site profissional.'),
 ('integracao', '🔗', 'Integração de sistemas e APIs', 'O mesmo dado digitado em três sistemas diferentes.',
  'Ligamos os sistemas pelas integrações oficiais de cada um (APIs, webhooks, arquivos). Você cadastra uma vez e a informação aparece onde precisa, com registro do que foi enviado.',
  'ERP com CRM, vendas com financeiro, planilha com sistema de gestão, avisos no Slack ou Teams.', 'Menos digitação, menos erro e informação sempre atualizada.',
  'Entregue: consulta de notas na SEFAZ com certificado digital no Nexus Contábil, em validação; integrações de chamados com Slack e n8n no Nexus Platform, em nova versão.', 'Olá! Quero conversar sobre integração entre os sistemas da minha empresa.'),
 ('automacao', '⚙️', 'Automação de processos', 'Tarefas repetitivas que consomem horas do time todo mês.',
  'Escolhemos o processo que mais pesa, desenhamos o fluxo e automatizamos as etapas mecânicas, mantendo uma pessoa responsável pelas decisões e aprovações.',
  'Cobrança de documentos, relatórios periódicos, aprovações, avisos por mensagem.', 'Tempo livre para análise e atendimento, com trilha de auditoria.',
  'Entregue: automações para o time de TI de um grupo com 6 empresas, com Slack e n8n.', 'Olá! Quero conversar sobre automação de um processo da minha empresa.'),
 ('ia', '🤖', 'Inteligência artificial aplicada', 'Atendimento e tarefas administrativas que dependem de leitura e triagem manual.',
  'Usamos IA onde ela ajuda de verdade: classificar solicitações, resumir conversas, organizar documentos e sugerir respostas. Sempre com revisão humana nas decisões importantes.',
  'Triagem de chamados, resumo de atendimentos, organização de documentos, assistentes internos.', 'Respostas mais rápidas e menos tempo em triagem.',
  'Em desenvolvimento: LeadNow, captura de leads em eventos com voz e IA. Ainda não lançado.', 'Olá! Quero conversar sobre como usar IA na minha empresa.'),
 ('dashboards', '📊', 'Dashboards e BI', 'Decisões baseadas em planilha montada à mão no fim do mês.',
  'Conectamos as fontes de dados, definimos com você os indicadores que importam e montamos painéis atualizados automaticamente, com exportação em Excel, CSV e PDF.',
  'Painel de vendas, DRE e fluxo de caixa, SLA de atendimento, produtividade da equipe.', 'Números a um clique, sem pedir para ninguém montar relatório.',
  'Entregue: DRE e fluxo de caixa no Nexus Contábil; relatórios de SLA no Nexus Platform, ambos em nova versão.', 'Olá! Quero conversar sobre dashboards para a minha empresa.'),
 ('gestao', '🗂️', 'Sistemas de gestão e ferramentas internas', 'Cada área controlando as coisas do seu jeito, em arquivos diferentes.',
  'Criamos ferramentas internas simples e seguras para pedidos, aprovações, estoque e acompanhamento, com perfis de acesso por função.',
  'Painel de solicitações, controle de ativos, fluxo de compras, gestão de contratos.', 'Processo padronizado e histórico de quem fez o quê.',
  'Entregue: plataforma de inventário de ativos para um grupo com 6 empresas.', 'Olá! Quero conversar sobre uma ferramenta interna de gestão.'),
 ('infra', '🖥️', 'Infraestrutura e consultoria de TI', 'Equipamentos sem controle, chamados sem histórico e dependência de uma pessoa só.',
  'Organizamos o atendimento, o inventário e as rotinas de suporte, e orientamos escolhas de ferramentas e segurança básica.',
  'Helpdesk com SLA, inventário de ativos, padronização de acessos, automações de rotina.', 'Suporte previsível e menos improviso.',
  'Entregue: estruturação da TI de um grupo com 6 empresas.', 'Olá! Quero conversar sobre infraestrutura e consultoria de TI.'),
 ('transformacao', '🚀', 'Modernização de processos', 'Processos antigos que travam o crescimento.',
  'Fazemos um diagnóstico, priorizamos o que dá ganho mais rápido e modernizamos por etapas, sem parar a operação.',
  'Troca de papel por fluxo digital, migração de planilhas para sistema, padronização entre filiais.', 'Crescer sem aumentar o trabalho manual na mesma proporção.',
  'Comece pelo diagnóstico e pelo checklist gratuitos do site.', 'Olá! Quero conversar sobre modernizar processos da minha empresa.'),
]
chips = ''.join(f'<a class="chip" href="#{i}" style="text-decoration:none">{t}</a>' for i, _, t, *_ in SV10)
blocks = ''
for n, (i, ico, t, prob, how, ex, ben, real, msg) in enumerate(SV10):
    bg = 'sec-white' if n % 2 == 0 else 'sec-lav'
    blocks += f'''<section id="{i}" class="{bg}" style="padding:3.2rem 5%"><div class="section-inner" style="max-width:960px">
<h2 class="section-title"><span aria-hidden="true">{ico}</span> {t}</h2>
<div class="two-col" style="margin-top:1.4rem">
<div class="callout"><b>O problema</b><p>{prob}</p></div>
<div class="callout"><b>Como funciona</b><p>{how}</p></div>
<div class="callout"><b>Exemplos de aplicação</b><p>{ex}</p></div>
<div class="callout"><b>Benefício</b><p>{ben}</p></div></div>
<p style="margin-top:1.2rem;font-size:.9rem;color:var(--gray-600)"><strong style="color:var(--indigo)">Na prática:</strong> {real}</p>
<p style="margin-top:1rem"><a class="btn-primary" href="{wa(msg)}" target="_blank" rel="noopener">Conversar sobre isso</a></p>
</div></section>
'''
ld = '<script type="application/ld+json">' + _j.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Service", "name": t, "description": prob, "areaServed": "BR",
     "provider": {"@type": "Organization", "name": "Nexus EF Business", "url": SITE}} for i, _, t, prob, *_ in SV10]}, ensure_ascii=False) + '</script>\n'
main = HERO('Serviços', 'Tecnologia sob medida para os desafios da sua empresa', 'Dez frentes de trabalho, cada uma com o problema que resolve, como funciona e um exemplo do que já entregamos. Serviços são desenvolvidos sob demanda. Os produtos próprios têm página à parte.', crumbs=[('Início', '/'), ('Serviços', None)]) + f'''
<section class="sec-white" style="padding:2.2rem 5% 0"><div class="section-inner" style="max-width:960px"><p class="section-eyebrow">Ir direto para</p><div style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:.6rem">{chips}</div></div></section>
{blocks}
<section class="sec-lav" style="padding:3.2rem 5%"><div class="section-inner" style="max-width:960px"><h2 class="section-title">Serviço sob demanda ou produto pronto?</h2>
<div class="two-col" style="margin-top:1.4rem"><div class="callout"><b>Sob demanda</b><p>Desenvolvemos para o seu caso. Escopo, prazo e valor definidos após o levantamento.</p></div>
<div class="callout"><b>Produtos próprios</b><p><a href="/nexus-contabil.html">Nexus Contábil</a> e <a href="/nexus-platform.html">Nexus Platform</a>, em nova versão com acesso antecipado. LeadNow está em desenvolvimento.</p></div></div>
<div style="margin-top:2rem">{CTA('Olá! Vim pela página de serviços da Nexus EF Business e gostaria de conversar.', 'Tem um processo que poderia ser automático?', 'Conte o seu desafio. A gente analisa, propõe e executa, do diagnóstico à solução em produção.')}</div></div></section>'''
wr('servicos.html', page('servicos.html', 'Serviços de tecnologia sob medida | Nexus EF Business', 'Sistemas personalizados, integrações, automação, IA, dashboards e consultoria de TI. Veja o problema que cada serviço resolve e exemplos reais.', main, ld, crumbs=[('Início', '/'), ('Serviços', None)], exit_popup=True))

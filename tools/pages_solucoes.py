# Páginas por segmento: /solucoes/. Conteúdo descreve possibilidades, não casos de clientes.
SEG = {
 'contabilidade': dict(nome='Escritórios de contabilidade', h1='Tecnologia para escritórios contábeis que querem atender mais com menos digitação',
  sub='Cadastro, notas, contratos e atendimento em um só lugar, com automações para a rotina da carteira.',
  dores=[('Dados espalhados', 'Cliente em um sistema, contrato em outro, notas em um terceiro.'), ('Rotina fiscal manual', 'Consultar notas, conferir e enviar documentos consome o mês.'),
         ('Atendimento disperso', 'Pedidos chegam por WhatsApp, e-mail e telefone, sem fila nem histórico.'), ('Pouca visão de rentabilidade', 'Difícil saber quanto cada cliente custa e rende.')],
  sols=[('Nexus Contábil', 'Plataforma própria de gestão contábil, hoje em nova versão com acesso antecipado.'), ('Integrações sob medida', 'Ligar o que o escritório já usa para cadastrar uma vez só.'),
        ('Portal do cliente', 'O cliente envia e consulta documentos sem depender de ligação.'), ('Painéis de gestão', 'Prazos, entregas e carga por responsável em uma tela.')],
  autos=['Aviso automático ao cliente quando um documento é recebido ou vence', 'Cobrança de documentos pendentes por mensagem, no dia certo', 'Criação de tarefas mensais por cliente, de acordo com o regime', 'Relatório mensal enviado ao gestor sem montar planilha'],
  integ=['Certificado digital', 'WhatsApp', 'E-mail', 'Planilhas', 'Sistemas de folha', 'Bancos (arquivos OFX)'],
  faq=[('O Nexus Contábil substitui o sistema que já uso?', 'Depende do que você usa hoje. Fazemos um levantamento e indicamos o que o Nexus cobre e o que continua em outro sistema, com integração.'),
       ('As obrigações fiscais são garantidas pela ferramenta?', 'Não. A ferramenta apoia a rotina, mas a responsabilidade técnica e a validação das obrigações continuam com o contador responsável.'),
       ('Dá para começar por uma parte?', 'Sim. Em geral começamos por um processo, como atendimento ou documentos, e evoluímos por etapas.')],
  msg='Olá! Tenho um escritório contábil e quero conversar sobre tecnologia e automação.', extra='<p style="margin-top:1rem"><a href="/nexus-contabil.html">Ver detalhes do Nexus Contábil</a></p>'),
 'clinicas': dict(nome='Clínicas e consultórios', h1='Menos papel e retrabalho na rotina da clínica',
  sub='Automações de agenda, comunicação e relatórios para a equipe administrativa ter mais tempo para os pacientes.',
  dores=[('Agenda com faltas', 'Pacientes esquecem consultas e o horário fica vazio.'), ('Cadastros duplicados', 'A mesma informação digitada na recepção, no faturamento e no convênio.'),
         ('Comunicação manual', 'Confirmações e avisos feitos um a um, por telefone ou WhatsApp.'), ('Indicadores escassos', 'Pouca visão de ocupação, retorno e faturamento por profissional.')],
  sols=[('Lembretes automáticos', 'Confirmação de consulta por mensagem, com resposta registrada.'), ('Integração de sistemas', 'Ligar agenda, faturamento e financeiro para digitar uma vez só.'),
        ('Painel de gestão', 'Ocupação, faltas e faturamento por período e por profissional.'), ('Ferramentas internas', 'Fluxos de aprovação e pedidos entre recepção, financeiro e coordenação.')],
  autos=['Mensagem de confirmação 24 horas antes e aviso de reagendamento', 'Lista de espera avisada quando abre um horário', 'Relatório semanal de faltas e ocupação para a coordenação', 'Envio de documentos administrativos sem papel'],
  integ=['Sistemas de agenda', 'WhatsApp', 'E-mail', 'Planilhas', 'Financeiro', 'Formulários online'],
  faq=[('Vocês acessam prontuários?', 'Não é necessário para a maioria das automações administrativas. Dados de saúde são sensíveis, então trabalhamos com o mínimo de dados e definimos o acesso com você.'),
       ('A solução cumpre a LGPD?', 'A conformidade depende do processo inteiro da clínica. Desenvolvemos com cuidados de segurança e acesso restrito, e recomendamos validar o tratamento de dados com um especialista jurídico.'),
       ('Funciona com o sistema que já usamos?', 'Depende de ele oferecer API ou exportação de dados. Avaliamos isso no início, antes de qualquer proposta.')],
  msg='Olá! Tenho uma clínica e quero conversar sobre automação da rotina administrativa.', extra=''),
 'advocacia': dict(nome='Escritórios de advocacia', h1='Organização e prazos sob controle no escritório de advocacia',
  sub='Ferramentas para acompanhar demandas, documentos e comunicação com clientes, sem planilhas soltas.',
  dores=[('Prazos na memória', 'Controle em agenda pessoal ou planilha que só uma pessoa entende.'), ('Documentos espalhados', 'Modelos, peças e anexos em pastas diferentes, difíceis de achar.'),
         ('Cliente sem atualização', 'Perguntas repetidas sobre andamento tomam tempo da equipe.'), ('Pouca visão da carteira', 'Difícil medir carga de trabalho e rentabilidade por área.')],
  sols=[('Painel de demandas', 'Quadro com responsável, prazo interno e status de cada demanda.'), ('Modelos e geração de documentos', 'Preenchimento automático de modelos a partir de um cadastro.'),
        ('Avisos ao cliente', 'Mensagens de andamento com texto revisado pelo escritório.'), ('Integrações', 'Ligar agenda, e-mail e armazenamento de arquivos.')],
  autos=['Alerta de prazo interno para o responsável e o supervisor', 'Geração de procuração e contrato a partir de um formulário', 'Resumo semanal de demandas abertas por advogado', 'Organização de anexos recebidos por e-mail em pastas por cliente'],
  integ=['Agenda', 'E-mail', 'Armazenamento em nuvem', 'Planilhas', 'WhatsApp', 'Assinatura eletrônica'],
  faq=[('Vocês oferecem orientação jurídica?', 'Não. Desenvolvemos tecnologia. Conteúdo jurídico e decisões continuam com os advogados do escritório.'),
       ('E o sigilo das informações?', 'Aplicamos controle de acesso e boas práticas de segurança, e definimos com você o que cada pessoa pode ver. Detalhes entram em contrato.'),
       ('Dá para integrar com sistemas de acompanhamento processual?', 'Depende da oferta de API ou exportação de cada fornecedor. Avaliamos caso a caso.')],
  msg='Olá! Tenho um escritório de advocacia e quero conversar sobre organização e automação.', extra=''),
 'comercio': dict(nome='Comércio e varejo', h1='Do pedido ao estoque, menos digitação e mais controle',
  sub='Integração entre loja, estoque, financeiro e atendimento para a operação rodar sem retrabalho.',
  dores=[('Estoque desencontrado', 'O que está no sistema não bate com o que está na prateleira.'), ('Vendas em vários canais', 'Loja física, site e redes sociais sem visão única.'),
         ('Conciliação manual', 'Pagamentos conferidos linha a linha no fim do mês.'), ('Atendimento no improviso', 'Dúvidas e pedidos misturados em conversas soltas.')],
  sols=[('Integração de canais', 'Pedidos de diferentes origens chegando em um único lugar.'), ('Painel de vendas e estoque', 'Indicadores diários de venda, giro e ruptura.'),
        ('Conciliação assistida', 'Cruzar vendas e recebimentos automaticamente e destacar diferenças.'), ('Atendimento organizado', 'Fila e histórico por cliente, com respostas padrão.')],
  autos=['Alerta de estoque mínimo para o comprador', 'Mensagem de acompanhamento de pedido ao cliente', 'Relatório diário de vendas enviado ao dono', 'Cadastro de produto feito uma vez e replicado nos canais'],
  integ=['ERP e sistemas de PDV', 'Marketplaces', 'Gateways de pagamento', 'Planilhas', 'WhatsApp', 'E-mail'],
  faq=[('Preciso trocar meu sistema de vendas?', 'Nem sempre. Se ele oferecer API ou exportação, podemos integrar. Se não, avaliamos alternativas com você.'),
       ('Quanto tempo leva uma integração?', 'Depende dos sistemas envolvidos. Damos um prazo só depois do levantamento, sem chute.'),
       ('Vocês fazem loja virtual?', 'Fazemos sites profissionais e integrações. Para lojas virtuais completas, avaliamos se uma plataforma pronta atende melhor.')],
  msg='Olá! Tenho um comércio e quero conversar sobre integração e automação.', extra=''),
 'empresas': dict(nome='Pequenas e médias empresas', h1='Sistema sob medida para a rotina da sua empresa, sem pagar por o que não usa',
  sub='Automação, integração e ferramentas internas para empresas que cresceram mais rápido que os seus processos.',
  dores=[('Planilhas como sistema', 'Informação crítica em arquivos que só uma pessoa domina.'), ('Sistemas que não se falam', 'ERP, CRM e financeiro exigem digitar os mesmos dados várias vezes.'),
         ('Aprovações por chat', 'Pedidos e aprovações sem registro de quem fez o quê.'), ('Indicadores atrasados', 'Para saber um número é preciso pedir para alguém montar.')],
  sols=[('Sistemas sob medida', 'Ferramentas internas desenhadas para o seu processo.'), ('Integrações e automações', 'Dados fluindo entre sistemas, com avisos e aprovações.'),
        ('Dashboards', 'Indicadores atualizados, sem montar relatório à mão.'), ('TI e helpdesk', 'Chamados, inventário e SLA organizados no Nexus Platform.')],
  autos=['Fluxo de aprovação de compras com registro de histórico', 'Integração entre ERP e planilhas de acompanhamento', 'Relatório diário ou semanal por e-mail para a diretoria', 'Cadastro único de clientes replicado nos sistemas'],
  integ=['ERP', 'CRM', 'Slack e Teams', 'Planilhas', 'n8n', 'APIs de terceiros'],
  faq=[('Por onde começar?', 'Pelo processo que mais consome tempo ou gera erro. O diagnóstico e o checklist do site ajudam a escolher.'),
       ('Os preços são fixos?', 'Não há tabela única. O valor depende do escopo e é definido depois do levantamento.'),
       ('Quem faz a manutenção depois?', 'Podemos acompanhar a evolução do sistema. Combinamos isso no início para não haver surpresa.')],
  msg='Olá! Tenho uma empresa e quero conversar sobre sistemas e automação.', extra='<p style="margin-top:1rem"><a href="/diagnostico.html">Faça o diagnóstico de automação</a> · <a href="/checklist-automacao.html">Checklist</a></p>'),
}
def _cal(items): return ''.join(f'<div class="callout"><b>{t}</b><p>{d}</p></div>' for t, d in items)
for slug, s in SEG.items():
    crumbs = [('Início', '/'), ('Soluções', '/solucoes/'), (s['nome'], None)]
    faq = ''.join(f'<details class="faq-item" style="margin-top:.7rem"><summary style="cursor:pointer;font-weight:700;color:var(--indigo)">{q}</summary><p style="margin-top:.6rem;color:var(--gray-600);line-height:1.8">{a}</p></details>' for q, a in s['faq'])
    ld = '<script type="application/ld+json">' + _j.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s['faq']]}, ensure_ascii=False) + '</script>\n'
    main = HERO(f'Soluções · {s["nome"]}', s['h1'], s['sub'], crumbs=crumbs) + f'''
<section class="sec-white" style="padding:3.5rem 5%"><div class="section-inner"><h2 class="section-title">Onde costuma doer</h2><div class="two-col" style="margin-top:1.5rem">{_cal(s['dores'])}</div></div></section>
<section class="sec-lav" style="padding:3.5rem 5%"><div class="section-inner"><h2 class="section-title">O que podemos desenvolver</h2><div class="two-col" style="margin-top:1.5rem">{_cal(s['sols'])}</div>
<p style="margin-top:1rem;font-size:.85rem;color:var(--gray-600)">Descrevemos possibilidades. Cada projeto começa com um levantamento do seu cenário.</p>{s['extra']}</div></section>
<section class="sec-white" style="padding:3.5rem 5%"><div class="section-inner" style="max-width:860px"><h2 class="section-title">Exemplos de automação</h2>
<ul style="margin:1.2rem 0 0 1.2rem;line-height:2;color:var(--gray-600)">{''.join(f'<li>{a}</li>' for a in s['autos'])}</ul>
<h2 class="section-title" style="margin-top:2.5rem">Integrações possíveis</h2><div style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem">{''.join(f'<span class="chip">{c}</span>' for c in s['integ'])}</div>
<p style="margin-top:.8rem;font-size:.85rem;color:var(--gray-600)">A viabilidade de cada integração depende de API ou exportação de dados do sistema envolvido.</p></div></section>
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:860px"><h2 class="section-title">Perguntas frequentes</h2><div style="margin-top:1rem">{faq}</div>
<div style="margin-top:2.5rem">{CTA(s['msg'], 'Vamos conversar sobre o seu caso?', 'Conte o seu cenário e a gente analisa com você, sem compromisso.')}</div></div></section>'''
    wr(f'solucoes/{slug}.html', page(f'solucoes/{slug}.html', f'{s["nome"]}: {s["h1"].split(",")[0][:55]} | Nexus EF Business', s['sub'], main, ld, crumbs=crumbs, exit_popup=True))
cards = ''.join(f'<a class="aud-card" href="/solucoes/{k}.html"><h3>{v["nome"]}</h3><p>{v["sub"]}</p><span class="go">Ver soluções →</span></a>' for k, v in SEG.items())
cards += '<a class="aud-card" href="/para/times-de-ti.html"><h3>Times de TI</h3><p>Helpdesk com SLA, inventário e integrações com Slack, Teams e n8n.</p><span class="go">Ver soluções →</span></a>'
cards += '<a class="aud-card" href="/para/empresas-de-eventos.html"><h3>Empresas de eventos</h3><p>Captura de leads e automação antes, durante e depois do evento.</p><span class="go">Ver soluções →</span></a>'
main = HERO('Soluções por segmento', 'Tecnologia pensada para o seu tipo de operação', 'Cada setor tem as suas dores. Veja como a Nexus pode ajudar no seu.', crumbs=[('Início', '/'), ('Soluções', None)]) + f'<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner"><div class="card-grid">{cards}</div></div></section>'
wr('solucoes/index.html', page('solucoes/', 'Soluções por segmento | Nexus EF Business', 'Soluções de tecnologia para contabilidade, clínicas, advocacia, comércio, empresas, times de TI e eventos.', main, crumbs=[('Início', '/'), ('Soluções', None)], exit_popup=True))

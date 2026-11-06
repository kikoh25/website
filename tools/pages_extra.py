# estudo de caso
cs=HERO('Projeto próprio','Conheça o projeto Nexus Contábil','Um sistema de gestão para escritórios de contabilidade que reúne fiscal, notas, contratos e atendimento em um só ambiente.',crumbs=[('Início','/'),('Blog','/blog/'),('Projeto Nexus Contábil',None)])+f'''
<article class="sec-white" style="padding:3rem 5% 5rem"><div class="section-inner article" style="max-width:760px">
<p>Este é um projeto próprio da Nexus EF Business, não um caso de cliente. Mostramos como o produto foi pensado e em que etapa ele está.</p>
<h2>O desafio</h2>
<p>Um escritório contábil trabalha com muitos sistemas ao mesmo tempo: o portal do governo para consultar notas, o das prefeituras para emitir NFS-e, planilhas de apuração, contratos em papel e conversas por WhatsApp. Cada um tem seu login, seu formato e seu prazo. O resultado é retrabalho, risco de erro e pouca visão do conjunto da carteira de clientes.</p>
<h2>O que desenvolvemos</h2>
<p>O Nexus Contábil reúne essa rotina em um ambiente único, com mais de 40 telas organizadas em frentes:</p>
<ul>
<li><strong>Documentos fiscais:</strong> consulta de notas na SEFAZ com certificado digital, importação de XML em lote e emissão de NFS-e pelo Portal Nacional (em validação).</li>
<li><strong>Apuração:</strong> apoio ao cálculo de ICMS, IPI, PIS e COFINS, com estimativas de IBS e CBS em evolução. A validação fiscal segue com o contador.</li>
<li><strong>Gestão do escritório:</strong> honorários, contratos com assinatura eletrônica simples, tarefas, calendário e equipe.</li>
<li><strong>Relacionamento com o cliente:</strong> portal do cliente com acesso por CNPJ e código.</li>
<li><strong>Inteligência fiscal:</strong> score de saúde fiscal por empresa, monitor de inconsistências, simulador de regime tributário e alerta de notas suspeitas.</li>
<li><strong>Relatórios:</strong> DRE, fluxo de caixa e comparativo anual, com exportação em CSV e Excel em módulos selecionados.</li>
</ul>
<h2>Decisões técnicas que importaram</h2>
<ul>
<li><strong>Separação por escritório:</strong> o sistema foi desenhado para cada escritório acessar apenas os seus dados. Esse isolamento ainda passa por validação técnica.</li>
<li><strong>Certificado digital:</strong> enviado pelo escritório e usado nas consultas à SEFAZ.</li>
<li><strong>Planos com módulos liberados por nível:</strong> o escritório contrata o que precisa e evolui depois.</li>
<li><strong>Cobrança prevista:</strong> integração com serviço de pagamento para assinaturas, ainda não liberada ao público.</li>
</ul>
<h2>O que o escritório ganha</h2>
<p>O objetivo é reduzir telas e logins, reunir as rotinas fiscais em um só lugar e dar uma visão da carteira que ajude a perceber riscos antes do prazo vencer. Nenhum resultado de clientes é divulgado, porque o produto está em acesso antecipado.</p>
<h2>Situação atual</h2>
<p>O Nexus Contábil está em uma nova versão. Escritórios interessados podem pedir acesso antecipado pelo WhatsApp.</p>
<p><a href="/nexus-contabil.html">Ver os módulos e os planos previstos</a></p>
{CTA('Olá! Li a página do projeto Nexus Contábil e quero pedir acesso antecipado.')}
</div></article>'''
ldcs=json.dumps({"@context":"https://schema.org","@type":"Article","headline":"Conheça o projeto Nexus Contábil","description":"Estudo de caso do Nexus Contábil, sistema de gestão para escritórios de contabilidade.","datePublished":"2026-11-05","inLanguage":"pt-BR","author":{"@type":"Organization","name":"Nexus EF Business"},"mainEntityOfPage":"https://nexusefbusiness.com.br/casos/sistema-contabil-34-modulos.html"},ensure_ascii=False)
wr('casos/sistema-contabil-34-modulos.html',page('casos/sistema-contabil-34-modulos.html','Conheça o projeto Nexus Contábil | Nexus EF Business','Como a Nexus EF Business desenvolve o Nexus Contábil, sistema de gestão para escritórios de contabilidade, hoje em acesso antecipado.',cs,f'<script type="application/ld+json">{ldcs}</script>\n',exit_popup=True))
# perguntas sobre automação
qa=[('O que é automação de processos?','É usar software para executar sozinho tarefas repetitivas que hoje alguém faz à mão, como copiar dados entre sistemas, gerar relatórios ou enviar avisos. O time passa a revisar exceções em vez de executar cada passo.'),
('Quais processos podem ser automatizados?','Os que acontecem com frequência, seguem regras claras e envolvem dados digitais. Exemplos comuns: cadastro e atualização de informações entre sistemas, emissão e envio de documentos, relatórios periódicos, avisos de prazo e triagem de chamados.'),
('Preciso trocar os sistemas que já uso?','Na maioria dos casos não. A automação costuma conectar o que você já tem, usando as integrações oficiais de cada sistema. A troca só faz sentido quando uma ferramenta não oferece nenhuma forma de integração.'),
('Automação substitui pessoas?','O objetivo é tirar o trabalho mecânico do time para sobrar tempo para análise, atendimento e decisão. As pessoas continuam responsáveis pelo que exige julgamento.'),
('Qual a diferença entre automação por API e RPA?','O RPA é um robô que imita cliques e digitação na tela de um sistema. A automação por API usa a conexão oficial entre os sistemas, em geral mais estável e rápida. Quando não há API, o RPA pode ser a saída.'),
('É seguro integrar sistemas?','Sim, quando se seguem boas práticas: chaves guardadas em local protegido, permissões mínimas por integração, registro de logs e atenção à LGPD quando há dados pessoais.'),
('Quanto tempo leva para ver resultado?','Depende do tamanho do processo. Trabalhamos em etapas curtas, de modo que a primeira parte já funcione cedo e você valide antes de seguir.'),
('Quanto custa automatizar um processo?','Depende do escopo, do número de sistemas envolvidos e da complexidade das regras. Depois de entender o seu processo, enviamos uma proposta com valor e prazo combinados antes de começar.'),
('Como sei se vale a pena?','Some as horas que o time gasta no processo por mês e multiplique pelo custo da hora. Você pode fazer essa conta no nosso diagnóstico em um minuto.'),
('Como começar?','Conte para nós qual processo mais consome o tempo do seu time. Fazemos um diagnóstico, propomos a solução e entregamos em etapas.')]
items=''.join(f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>\n' for q,a in qa)
ldq=json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]},ensure_ascii=False)
fq=HERO('Perguntas frequentes','Perguntas sobre automação de processos','As dúvidas mais comuns de quem está pensando em automatizar tarefas e integrar sistemas na empresa.',crumbs=[('Início','/'),('Blog','/blog/'),('Perguntas sobre automação',None)])+f'''
<section class="sec-white" style="padding:3rem 5% 5rem"><div class="section-inner" style="max-width:820px">
{items}
<p style="margin-top:2rem;color:var(--gray-600)">Quer fazer a conta do seu caso? Use o <a href="/diagnostico.html" style="color:var(--purple);font-weight:600">diagnóstico de automação</a>.</p>
{CTA('Olá! Li as perguntas sobre automação e quero conversar sobre o meu processo.')}
</div></section>'''
wr('perguntas-sobre-automacao.html',page('perguntas-sobre-automacao.html','Perguntas sobre automação de processos | Nexus EF Business','Respostas curtas sobre automação de processos, integração de sistemas, segurança, prazo e custo.',fq,f'<script type="application/ld+json">{ldq}</script>\n',exit_popup=True))

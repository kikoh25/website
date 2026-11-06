# Páginas novas: ferramentas, checklist, públicos, sobre, status, offline, inglês, PWA.
import json as _j

def slider(i, label, mn, mx, step, val, unit='', hint=''):
    return (f'<div><label for="{i}">{label}</label><div class="row"><input type="range" id="{i}" min="{mn}" max="{mx}" step="{step}" value="{val}" aria-describedby="{i}V">'
            f'<output id="{i}V" data-unit="{unit}"></output></div>' + (f'<p class="hint">{hint}</p>' if hint else '') + '</div>')

CALC_JS = '''<script>
(function(){
  var $=function(i){return document.getElementById(i)};
  var brl=function(n){return n.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0})};
  var num=function(n){return Math.round(n).toLocaleString('pt-BR')};
  var brl2=function(n){return n.toLocaleString('pt-BR',{style:'currency',currency:'BRL'})};
  var dec=function(n){return n.toLocaleString('pt-BR',{maximumFractionDigits:1})};
  var money=function(n){return n<1000?brl2(n):brl(n)};
  var hrs=function(n){return (n<10?dec(n):num(n))+' h'};
  var ids=%IDS%;
  function val(i){return +$(i).value}
  function show(){ids.forEach(function(i){var o=$(i+'V'),u=o.getAttribute('data-unit'),v=val(i);o.textContent=u==='R$'?'R$ '+v:v+u})}
  function run(){show();%CALC%}
  ids.forEach(function(i){$(i).addEventListener('input',run)});run();
})();
</script>'''

def calc_page(path, title, desc, h1, sub, sliders, result_html, calc_js, ids, crumb):
    main = HERO('Ferramenta grátis', h1, sub, crumbs=[('Início', '/'), ('Ferramentas', '/ferramentas/'), (crumb, None)]) + f'''
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:860px">
<form class="tool-form" onsubmit="return false">{''.join(sliders)}</form>
<div class="result-box" role="status" aria-live="polite">{result_html}</div>
<p style="margin-top:2rem"><a href="/ferramentas/">Ver outras ferramentas</a></p>
</div></section>''' + CALC_JS.replace('%IDS%', _j.dumps(ids)).replace('%CALC%', calc_js)
    wr(path, page(path, title, desc, main, crumbs=[('Início', '/'), ('Ferramentas', '/ferramentas/'), (crumb, None)], exit_popup=True))

def stat(label, idn, accent=False):
    return f'<div><p style="font-size:.85rem;color:rgba(255,255,255,.75)">{label}</p><p id="{idn}" style="font-family:\'Lora\',serif;font-size:1.9rem;font-weight:700{";color:#C4B5FD" if accent else ""}"></p></div>'

def stats(*items):
    return '<div style="display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin-top:1rem">' + ''.join(items) + '</div>'

# ---------- custo do chamado ----------
calc_page('ferramentas/custo-chamado-ti.html', 'Calculadora: custo de um chamado de TI | Nexus EF Business',
  'Descubra quanto custa cada chamado de suporte e quanto a sua empresa pode economizar com helpdesk e automação.',
  'Quanto custa cada chamado de TI?', 'Informe o volume e o tempo de atendimento e veja o custo mensal do suporte e o quanto dá para reduzir.',
  [slider('ch', 'Chamados por mês', 20, 2000, 10, 200), slider('mi', 'Minutos médios por chamado', 5, 120, 5, 25, ' min'),
   slider('hc', 'Custo médio da hora do atendente', 15, 200, 5, 45, 'R$'),
   slider('rp', 'Chamados repetitivos (senha, acesso, dúvida comum)', 5, 80, 5, 40, '%', 'Os que seguem sempre o mesmo roteiro.'),
   slider('ev', 'Parte desses que automação ou base de conhecimento resolve', 10, 90, 5, 50, '%')],
  '<p class="kicker">Estimativa com base nos números informados</p>' + stats(
    stat('Custo por chamado', 'o1'), stat('Custo mensal do suporte', 'o2'), stat('Horas por mês', 'o3'), stat('Economia possível por ano', 'o4', True))
  + '<p class="note">Cálculo: horas = chamados x minutos / 60. Economia = chamados repetitivos x percentual evitável x custo por chamado x 12. São estimativas, não promessas de resultado.</p>'
  '<a id="cta" class="btn-primary" target="_blank" rel="noopener" href="#" style="margin-top:1.2rem">Quero reduzir esse custo</a>',
  '''var c=val('ch'),m=val('mi'),h=val('hc'),r=val('rp')/100,e=val('ev')/100;var hh=c*m/60,cm=hh*h,cc=cm/c,eco=c*r*e*cc*12;
$('o1').textContent=brl2(cc);$('o2').textContent=money(cm);$('o3').textContent=hrs(hh);$('o4').textContent=money(eco);
$('cta').href='https://wa.me/%s?text='+encodeURIComponent('Olá! Usei a calculadora de custo de chamado: '+num(c)+' chamados por mês, custo de '+brl2(cc)+' cada, economia estimada de '+money(eco)+' por ano. Quero conversar sobre helpdesk e automação.');''' % PHONE,
  ['ch', 'mi', 'hc', 'rp', 'ev'], 'Custo de um chamado de TI')

# ---------- retrabalho ----------
calc_page('ferramentas/custo-retrabalho.html', 'Calculadora: custo do retrabalho e erros manuais | Nexus EF Business',
  'Calcule quanto os erros de digitação e a conferência manual custam por mês na sua operação.',
  'Quanto o retrabalho custa por mês?', 'Erros de digitação e conferência manual viram horas perdidas. Veja o tamanho disso na sua rotina.',
  [slider('op', 'Operações manuais por mês (lançamentos, cadastros, conferências)', 50, 5000, 50, 800), slider('er', 'Percentual com erro ou retrabalho', 1, 30, 1, 6, '%'),
   slider('mc', 'Minutos para encontrar e corrigir cada erro', 5, 90, 5, 20, ' min'), slider('hr', 'Custo médio da hora de trabalho', 15, 200, 5, 40, 'R$'),
   slider('rd', 'Redução de erros com automação ou validação', 20, 95, 5, 70, '%', 'Depende do processo. Use um valor conservador.')],
  '<p class="kicker">Estimativa com base nos números informados</p>' + stats(
    stat('Erros por mês', 'o1'), stat('Horas perdidas por mês', 'o2'), stat('Custo por mês', 'o3'), stat('Economia possível por ano', 'o4', True))
  + '<p class="note">Cálculo: erros = operações x percentual. Horas = erros x minutos / 60. Economia = custo mensal x redução x 12. Não inclui prejuízos indiretos, como multas e perda de clientes. São estimativas.</p>'
  '<a id="cta" class="btn-primary" target="_blank" rel="noopener" href="#" style="margin-top:1.2rem">Quero eliminar esse retrabalho</a>',
  '''var o=val('op'),p=val('er')/100,m=val('mc'),h=val('hr'),r=val('rd')/100;var er=o*p,hh=er*m/60,cm=hh*h,eco=cm*r*12;
$('o1').textContent=(er<10?dec(er):num(er))+(Math.abs(er-1)<0.05?' erro':' erros');$('o2').textContent=hrs(hh);$('o3').textContent=money(cm);$('o4').textContent=money(eco);
$('cta').href='https://wa.me/%s?text='+encodeURIComponent('Olá! Usei a calculadora de retrabalho: cerca de '+(er<10?dec(er):num(er))+' erros por mês, '+money(cm)+' de custo mensal. Quero conversar sobre como reduzir isso.');''' % PHONE,
  ['op', 'er', 'mc', 'hr', 'rd'], 'Custo do retrabalho')

# ---------- comparador ----------
QS = [
 ('Quantas pessoas vão usar a solução?', [('Até 3', 'p'), ('De 4 a 20', 'e'), ('Mais de 20', 's')]),
 ('Como é o seu processo hoje?', [('Simples e muda pouco', 'p'), ('Segue um padrão de mercado', 'e'), ('É específico do meu negócio', 's')]),
 ('Você precisa ligar sistemas que já usa?', [('Não', 'p'), ('Um ou dois, com conectores prontos', 'e'), ('Vários, ou sistemas próprios', 's')]),
 ('Qual a sua urgência?', [('Preciso começar hoje', 'p'), ('Algumas semanas', 'e'), ('Posso esperar por algo certo', 's')]),
 ('Quanto os erros e o retrabalho pesam?', [('Quase nada', 'p'), ('Incomodam', 'e'), ('Custam caro todo mês', 's')]),
 ('Pretende crescer ou vender essa solução?', [('Não', 'p'), ('Crescer devagar', 'e'), ('Sim, quero escalar ou virar produto', 's')]),
]
qh = ''
for n, (q, opts) in enumerate(QS):
    qh += f'<div class="quiz-q"><fieldset><legend>{n+1}. {q}</legend>' + ''.join(
        f'<label class="quiz-opt"><input type="radio" name="q{n}" value="{v}" /> <span>{t}</span></label>' for t, v in opts) + '</fieldset></div>'
RES = {
 'p': ('Planilha ou ferramenta pronta', 'O seu cenário é simples. Comece com uma planilha bem organizada ou uma ferramenta pronta e barata. Quando o volume ou os erros crescerem, volte aqui.'),
 'e': ('Sistema de prateleira (ERP ou SaaS)', 'Há padrão de mercado e poucos casos especiais. Um sistema pronto, com integrações, costuma resolver mais rápido e com menor custo inicial.'),
 's': ('Solução sob medida', 'O seu processo é específico, tem integrações ou pesa no resultado. Um sistema sob medida evita adaptar a empresa ao software e cresce junto com você.'),
}
main = HERO('Ferramenta grátis', 'Planilha, sistema pronto ou sob medida?', 'Responda 6 perguntas rápidas e veja qual caminho tende a fazer mais sentido para o seu caso.',
            crumbs=[('Início', '/'), ('Ferramentas', '/ferramentas/'), ('Comparador de solução', None)]) + f'''
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:860px">
<div class="quiz-bar" aria-hidden="true"><i id="qbar"></i></div>
<form id="quiz" style="display:grid;gap:1rem" onsubmit="return false">{qh}</form>
<div id="qres" class="result-box" role="status" aria-live="polite" hidden>
 <p class="kicker">Caminho que combina mais com você</p>
 <p id="qt" style="font-family:'Lora',serif;font-size:1.7rem;font-weight:700;margin-top:.5rem"></p>
 <p id="qd" style="margin-top:.7rem;line-height:1.8;color:rgba(255,255,255,.88)"></p>
 <p id="qh" style="margin-top:.7rem;line-height:1.8;color:#C4B5FD"></p>
 <p class="note">Resultado orientativo, baseado em regras simples. Cada caso tem particularidades que merecem uma conversa.</p>
 <a id="qcta" class="btn-primary" target="_blank" rel="noopener" href="#" style="margin-top:1.2rem">Conversar sobre o meu caso</a>
</div>
<p style="margin-top:2rem"><a href="/ferramentas/">Ver outras ferramentas</a></p>
</div></section>
<script>
(function(){{
  var R={_j.dumps({k: list(v) for k, v in RES.items()}, ensure_ascii=False)};
  var f=document.getElementById('quiz'),res=document.getElementById('qres'),bar=document.getElementById('qbar');
  function upd(){{
    var a=[],s={{p:0,e:0,s:0}};
    for(var i=0;i<{len(QS)};i++){{var c=f.querySelector('input[name=q'+i+']:checked');if(c){{a.push(c.value);s[c.value]++}}}}
    bar.style.width=(a.length/{len(QS)}*100)+'%';
    if(a.length<{len(QS)}){{res.hidden=true;return}}
    var N={{p:'planilha ou ferramenta pronta',e:'sistema de prateleira',s:'solução sob medida'}},rank={{p:0,e:1,s:2}};
    var ord=['s','e','p'].sort(function(x,y){{return s[y]-s[x]}});var top=ord[0],sec=ord[1];
    if(s[top]-s[sec]>=2){{document.getElementById('qt').textContent=R[top][0];document.getElementById('qd').textContent=R[top][1];document.getElementById('qh').textContent='';var res0=R[top][0]}}
    else{{var simple=rank[top]<rank[sec]?top:sec,compl=simple===top?sec:top;var res0='Caminho híbrido';
      document.getElementById('qt').textContent=res0;
      document.getElementById('qd').textContent='Suas respostas ficaram divididas entre '+N[top]+' e '+N[sec]+'. Isso é comum e faz sentido.';
      document.getElementById('qh').textContent='Uma boa rota: use '+N[simple]+' para o que é padrão e reserve '+N[compl]+' para as partes específicas do seu negócio, integrando as duas.'}}
    document.getElementById('qcta').href='https://wa.me/{PHONE}?text='+encodeURIComponent('Olá! Fiz o comparador de solução no site e o resultado foi: '+res0+'. Quero conversar sobre o meu caso.');
    res.hidden=false;res.scrollIntoView({{behavior:'smooth',block:'nearest'}});
  }}
  f.addEventListener('change',upd);
}})();
</script>'''
wr('ferramentas/comparador-solucao.html', page('ferramentas/comparador-solucao.html', 'Comparador: planilha, ERP ou sob medida? | Nexus EF Business',
   'Responda 6 perguntas e descubra se o seu caso pede planilha, sistema pronto ou solução sob medida.', main,
   crumbs=[('Início', '/'), ('Ferramentas', '/ferramentas/'), ('Comparador de solução', None)], exit_popup=True))

# ---------- índice de ferramentas ----------
T = [('/diagnostico.html', '⏱️', 'Diagnóstico de automação', 'Estime as horas e o custo das tarefas repetitivas do seu time.'),
     ('/ferramentas/custo-chamado-ti.html', '🎫', 'Custo de um chamado de TI', 'Quanto custa cada atendimento e quanto dá para economizar.'),
     ('/ferramentas/custo-retrabalho.html', '🔁', 'Custo do retrabalho', 'Quanto os erros de digitação e conferência custam por mês.'),
     ('/ferramentas/comparador-solucao.html', '⚖️', 'Planilha, ERP ou sob medida?', '6 perguntas para escolher o caminho certo.'),
     ('/checklist-automacao.html', '✅', 'Checklist de automação', '10 sinais de que é hora de automatizar. Baixe em PDF.'),
     ('/materiais/apresentacao-nexus-ef-business.pdf', '📄', 'Apresentação da Nexus (PDF)', 'Resumo de uma página para compartilhar com sua equipe.')]
tc = ''.join(f'<a class="tool-card" href="{u}"><div class="ico" aria-hidden="true">{i}</div><h2>{t}</h2><p>{d}</p><span class="go">Abrir →</span></a>' for u, i, t, d in T)
main = HERO('Ferramentas grátis', 'Faça as contas antes de decidir', 'Calculadoras e guias rápidos. Sem cadastro, sem e-mail, tudo roda no seu navegador.', crumbs=[('Início', '/'), ('Ferramentas', None)]) + \
    f'<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner"><div class="card-grid">{tc}</div></div></section>'
wr('ferramentas/index.html', page('ferramentas/', 'Ferramentas grátis | Nexus EF Business', 'Calculadoras e guias grátis para medir o custo de processos manuais, chamados de TI e retrabalho.', main,
   crumbs=[('Início', '/'), ('Ferramentas', None)], exit_popup=True))

# ---------- checklist ----------
CK = [('Copiamos os mesmos dados em mais de um sistema.', 'Digitar duas vezes é custo e risco de erro.'),
      ('Planilhas viraram o sistema oficial da empresa.', 'Quando a planilha tem dono único, o risco é alto.'),
      ('Relatórios são montados à mão todo mês.', 'Horas que voltam a cada fechamento.'),
      ('Perguntamos a mesma coisa para o time de TI toda semana.', 'Senha, acesso, dúvida comum: dá para resolver sem chamado.'),
      ('Não sabemos quais equipamentos ou licenças temos.', 'Sem inventário, compra e auditoria viram adivinhação.'),
      ('Prazos e SLAs dependem da memória das pessoas.', 'O que não é medido atrasa sem ninguém notar.'),
      ('Aprovações andam por WhatsApp e e-mail.', 'Sem trilha de quem aprovou o quê e quando.'),
      ('Nossos sistemas não conversam entre si.', 'Uma integração pode eliminar horas de trabalho manual.'),
      ('Para saber um número, precisamos pedir para alguém.', 'Indicadores devem estar a um clique.'),
      ('Crescer significaria contratar mais gente para o mesmo trabalho.', 'Processo que não escala pede automação.')]
items = ''.join(f'<li><input type="checkbox" id="c{i}" /><label for="c{i}"><strong>{t}</strong><br>{d}</label></li>' for i, (t, d) in enumerate(CK))
main = HERO('Guia grátis', 'Checklist: sua empresa precisa automatizar?', 'Marque o que acontece na sua rotina. Quanto mais marcações, maior a chance de ganho com automação.', crumbs=[('Início', '/'), ('Checklist de automação', None)]) + f'''
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:860px">
<ul class="check-list">{items}</ul>
<div class="result-box" role="status" aria-live="polite">
 <p class="kicker">Seu resultado</p>
 <p id="ckn" style="font-family:'Lora',serif;font-size:2rem;font-weight:700;margin-top:.4rem">0 de {len(CK)}</p>
 <p id="ckm" style="margin-top:.6rem;line-height:1.8;color:rgba(255,255,255,.88)"></p>
 <p class="note">Orientação geral, sem valor de diagnóstico. Cada empresa é diferente.</p>
 <div style="display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.2rem">
  <a id="ckc" class="btn-primary" target="_blank" rel="noopener" href="#">Conversar com a Nexus</a>
  <a class="btn-ghost" href="/materiais/checklist-automacao-nexus.pdf" download style="color:#fff;border-color:rgba(255,255,255,.4)">Baixar em PDF</a>
 </div>
</div>
</div></section>
<script>
(function(){{
  var b=document.querySelectorAll('.check-list input'),n=document.getElementById('ckn'),m=document.getElementById('ckm'),c=document.getElementById('ckc');
  function u(){{var k=0;b.forEach(function(x){{if(x.checked)k++}});n.textContent=k+' de {len(CK)}';
    m.textContent=k===0?'Nenhum item marcado ainda. Marque o que acontece na sua rotina para ver uma orientação.':k<=2?'Poucos sinais marcados. Pode haver pontos isolados de melhoria, vale olhar os itens marcados com calma.':k<=6?'Há sinais relevantes. Escolher um ou dois processos para começar pode trazer ganho rápido.':'Muitos sinais marcados. Um diagnóstico pode ajudar a priorizar por onde começar.';
    c.href='https://wa.me/{PHONE}?text='+encodeURIComponent(k?'Olá! Fiz o checklist de automação e marquei '+k+' de {len(CK)} itens. Quero conversar sobre o meu caso.':'Olá! Vi o checklist de automação no site e quero conversar sobre o meu caso.')}}
  b.forEach(function(x){{x.addEventListener('change',u)}});u();
}})();
</script>'''
wr('checklist-automacao.html', page('checklist-automacao.html', 'Checklist: sua empresa precisa automatizar? | Nexus EF Business',
   '10 sinais de que a sua empresa precisa automatizar processos. Marque online e baixe o checklist em PDF.', main,
   crumbs=[('Início', '/'), ('Checklist de automação', None)], exit_popup=True))

# ---------- páginas por público ----------
def audience(slug, name, eb, h1, sub, pains, sols, status_note, msg, extra=''):
    pc = ''.join(f'<div class="callout"><b>{t}</b><p>{d}</p></div>' for t, d in pains)
    sc = ''.join(f'<div class="callout"><b>{t}</b><p>{d}</p></div>' for t, d in sols)
    main = HERO(eb, h1, sub, crumbs=[('Início', '/'), (name, None)]) + f'''
<section class="sec-white" style="padding:3.5rem 5%"><div class="section-inner">
<h2 class="section-title">Onde costuma doer</h2><div class="two-col" style="margin-top:1.5rem">{pc}</div></div></section>
<section class="sec-lav" style="padding:3.5rem 5%"><div class="section-inner">
<h2 class="section-title">Como a Nexus ajuda</h2><div class="two-col" style="margin-top:1.5rem">{sc}</div>
<p style="margin-top:1.5rem;font-size:.88rem;color:var(--gray-600)">{status_note}</p>{extra}
<div style="margin-top:2rem">{CTA(msg)}</div></div></section>'''
    wr(f'para/{slug}.html', page(f'para/{slug}.html', f'{h1} | Nexus EF Business', sub, main, crumbs=[('Início', '/'), (name, None)], exit_popup=True))

audience('empresas-de-eventos', 'Empresas de eventos', 'Para empresas de eventos', 'Cada contato do evento vira oportunidade',
  'Captura de leads e automação antes, durante e depois do evento, sem planilha solta nem cartão de visita perdido.',
  [('Leads perdidos', 'Cartões, fichas e conversas rápidas que nunca chegam ao comercial.'),
   ('Follow-up lento', 'Quando o contato é feito, o interesse já esfriou.'),
   ('Dados sem padrão', 'Cada equipe anota de um jeito e ninguém consegue consolidar.'),
   ('Pouco retorno medido', 'Difícil provar ao patrocinador quantos contatos o evento gerou.')],
  [('LeadNow, em desenvolvimento', 'Captura de leads com voz e IA durante o evento. Ainda não lançado. Podemos conversar sobre acesso antecipado.'),
   ('Integração com CRM e planilhas', 'Cada lead cai direto onde o comercial trabalha.'),
   ('Mensagens automáticas', 'Retorno imediato por e-mail ou WhatsApp, com texto aprovado por você.'),
   ('Painel pós-evento', 'Números consolidados para prestar contas a patrocinadores.')],
  'O LeadNow ainda está em desenvolvimento e não é um produto disponível. Automações e integrações sob medida podem ser feitas agora.',
  'Olá! Trabalho com eventos e quero conversar sobre captura de leads e automação.')
audience('times-de-ti', 'Times de TI', 'Para times de TI', 'Chamados, ativos e SLA sob controle',
  'O Nexus Platform organiza o suporte, o inventário e os indicadores do time de TI em um único painel.',
  [('Chamados por todo lado', 'Pedidos chegam por chat, e-mail e corredor, sem fila nem prioridade.'),
   ('SLA no escuro', 'Ninguém sabe o que está perto de estourar até estourar.'),
   ('Inventário desatualizado', 'Equipamentos e licenças em planilhas que ninguém confia.'),
   ('Sem prova de resultado', 'Difícil mostrar à diretoria o volume e a qualidade do atendimento.')],
  [('Nexus Platform', 'Helpdesk com SLA, CSAT, inventário de ativos, base de conhecimento e relatórios.'),
   ('Integrações', 'Slack, Teams, n8n e outras, para abrir e acompanhar chamados onde o time já está.'),
   ('Demonstração com dados fictícios', 'Veja as telas do produto antes de falar com a gente.'),
   ('Automação de rotina', 'Senhas, acessos e respostas comuns resolvidas por fluxo.')],
  'O Nexus Platform está em nova versão, com acesso antecipado. Pergunte pela disponibilidade e pelos planos.',
  'Olá! Sou de TI e quero conhecer o Nexus Platform.',
  '<p style="margin-top:1rem"><a href="/nexus-platform.html">Ver detalhes do Nexus Platform</a> · <a href="/demo-platform.html">Ver a demonstração</a></p>')

# ---------- sobre ----------
TL = [('Infraestrutura de TI', 'Estruturação da TI de um grupo com 6 empresas: helpdesk, inventário de ativos e automações.'),
      ('ERP financeiro', 'Sistema financeiro com ecossistema de bots no Slack para aprovações e avisos.'),
      ('Nexus Platform', 'Plataforma de helpdesk e inventário, com SLA, CSAT, base de conhecimento e integrações.'),
      ('LeadNow, em desenvolvimento', 'Captura de leads em eventos com voz e IA. Ainda não lançado.'),
      ('Nexus Contábil', 'Sistema de gestão contábil com mais de 40 telas e integrações fiscais, em nova versão.'),
      ('Agora', 'Colocando os produtos em nova versão e atendendo projetos sob medida.')]
tl = ''.join(f'<li><span class="when">{"Etapa " + str(i+1) if t != "Agora" else "Agora"}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(TL))
VAL = [('Entrega real', 'Prometemos só o que o produto faz hoje e dizemos quando algo ainda está em desenvolvimento.'),
       ('Conversa direta', 'Você fala com quem desenvolve, sem intermediários.'),
       ('Simplicidade', 'Tecnologia consolidada e fácil de manter, para o sistema durar.')]
vc = ''.join(f'<div class="callout"><b>{t}</b><p>{d}</p></div>' for t, d in VAL)
tech = ''.join(f'<span class="chip">{c}</span>' for c in ['NestJS', 'Next.js', 'TypeScript', 'Node.js', 'Python', 'PostgreSQL', 'Prisma', 'Docker', 'Cloudflare', 'n8n', 'Slack API', 'Linux'])
main = HERO('Sobre', 'Quem está por trás da Nexus EF Business', 'Erick, fundador e desenvolvedor. Transformo problemas de empresa em sistemas que funcionam.', crumbs=[('Início', '/'), ('Sobre', None)]) + f'''
<section class="sec-white" style="padding:3.5rem 5%"><div class="section-inner" style="max-width:860px">
<p style="font-size:1.05rem;line-height:1.9;color:var(--gray-600)">Sou desenvolvedor full-stack e fundei a Nexus EF Business para criar software sob medida, integrações e automações para empresas. Minha trajetória passa por infraestrutura de TI, sistemas financeiros e produtos próprios. Atuo sozinho, o que significa conversa direta, decisões rápidas e responsabilidade de ponta a ponta.</p>
<h2 class="section-title" style="margin-top:2.5rem">Como eu trabalho</h2><div class="two-col" style="margin-top:1.2rem">{vc}</div></div></section>
<section class="sec-lav" style="padding:3.5rem 5%"><div class="section-inner" style="max-width:860px">
<h2 class="section-title">O que já construímos</h2>
<ol class="timeline">{tl}</ol>
<h2 class="section-title" style="margin-top:3rem">Tecnologias</h2>
<div style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem">{tech}</div>
<div style="margin-top:2.5rem">{CTA('Olá! Vi a página Sobre e quero conversar sobre um projeto.', 'Vamos conversar sobre o seu projeto?', 'Fale direto com o fundador.')}</div>
</div></section>'''
ld = '<script type="application/ld+json">' + _j.dumps({"@context": "https://schema.org", "@type": "AboutPage", "name": "Sobre a Nexus EF Business", "url": SITE + "/sobre.html"}, ensure_ascii=False) + '</script>\n'
wr('sobre.html', page('sobre.html', 'Sobre o fundador | Nexus EF Business', 'Conheça a trajetória do fundador da Nexus EF Business e o que já construímos em sistemas, integrações e automação.', main, ld,
   crumbs=[('Início', '/'), ('Sobre', None)], exit_popup=True))

# ---------- status ----------
main = HERO('Status', 'Status do site e dos produtos', 'Verificação feita agora, no seu navegador.', crumbs=[('Início', '/'), ('Status', None)]) + '''
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:760px;display:grid;gap:.8rem">
<div class="status-row"><b>Site (página inicial)</b><span class="pill" id="s1">Verificando</span></div>
<div class="status-row"><b>Blog</b><span class="pill" id="s2">Verificando</span></div>
<div class="status-row"><b>Ferramentas</b><span class="pill" id="s3">Verificando</span></div>
<div class="status-row"><b>Nexus Contábil</b><span class="pill warn">Nova versão em preparação</span></div>
<div class="status-row"><b>Nexus Platform</b><span class="pill warn">Nova versão em preparação</span></div>
<div class="status-row"><b>LeadNow</b><span class="pill">Em desenvolvimento</span></div>
<p style="font-size:.85rem;color:var(--gray-600);margin-top:1rem">As três primeiras linhas testam o carregamento das páginas neste momento. Os produtos são atualizados manualmente.</p>
</div></section>
<script>
(function(){
  function chk(id,u){var e=document.getElementById(id);fetch(u,{cache:'no-store'}).then(function(r){e.textContent=r.ok?'Operacional':'Com problema';e.className='pill '+(r.ok?'ok':'bad')}).catch(function(){e.textContent='Sem resposta';e.className='pill bad'})}
  chk('s1','/');chk('s2','/blog/');chk('s3','/ferramentas/');
})();
</script>'''
wr('status.html', page('status.html', 'Status | Nexus EF Business', 'Status do site e dos produtos da Nexus EF Business.', main, crumbs=[('Início', '/'), ('Status', None)]))

# ---------- offline ----------
wr('offline.html', '''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Sem conexão | Nexus EF Business</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#1E1B4B;color:#fff;font-family:system-ui,sans-serif;text-align:center;padding:2rem}h1{font-size:1.8rem}p{color:#DDD6FE;line-height:1.7}button{background:#7C3AED;color:#fff;border:0;border-radius:10px;padding:.8rem 1.6rem;font-size:1rem;cursor:pointer}</style></head>
<body><main><h1>Você está sem conexão</h1><p>Verifique a internet e tente de novo.</p><button onclick="location.reload()">Tentar novamente</button></main></body></html>''')

# ---------- PWA ----------
wr('manifest.webmanifest', _j.dumps({"name": "Nexus EF Business", "short_name": "Nexus EF", "description": "Sistemas, automação e integrações para empresas.",
   "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#1E1B4B", "theme_color": "#1E1B4B", "lang": "pt-BR",
   "icons": [{"src": "/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False, indent=1))
wr('sw.js', '''// Service worker mínimo: só mostra a página offline quando a navegação falha. Não guarda conteúdo.
const OFF='offline-v1';
self.addEventListener('install',e=>{e.waitUntil(caches.open(OFF).then(c=>c.add('/offline.html')).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==OFF).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).catch(()=>caches.match('/offline.html')))}});
''')

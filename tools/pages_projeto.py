# Página "Apresente seu projeto": monta um resumo estruturado no navegador. Nada é enviado sem ação do usuário.
SEGS = ['Contabilidade', 'Clínica ou consultório', 'Advocacia', 'Comércio ou varejo', 'Empresa de serviços', 'Pequena ou média empresa', 'Time de TI', 'Eventos', 'Outro']
NEED = ['Sistema sob medida', 'Automação de processos', 'Integração de sistemas', 'Inteligência artificial', 'Dashboard ou relatórios', 'Site profissional', 'Consultoria de TI', 'Ainda não sei']
PRIO = ['Alta: preciso resolver logo', 'Média: nos próximos meses', 'Baixa: estou pesquisando']
USERS = ['1 a 5', '6 a 20', '21 a 100', 'Mais de 100']
def opts(l): return ''.join(f'<option value="{o}">{o}</option>' for o in l)
def fld(i, label, inner, hint=''): return f'<div class="pf"><label for="{i}">{label}</label>{inner}' + (f'<p class="hint">{hint}</p>' if hint else '') + '</div>'
form = ''.join([
 fld('pseg', 'Segmento da empresa', f'<select id="pseg" required><option value="">Selecione</option>{opts(SEGS)}</select>'),
 fld('pneed', 'O que você procura?', f'<select id="pneed" required><option value="">Selecione</option>{opts(NEED)}</select>'),
 fld('pprob', 'Qual problema você quer resolver?', '<textarea id="pprob" rows="3" required placeholder="Ex.: digitamos os mesmos dados em três sistemas"></textarea>'),
 fld('psol', 'Como imagina a solução? (opcional)', '<textarea id="psol" rows="3" placeholder="Ex.: um painel que reúna tudo"></textarea>'),
 fld('psis', 'Sistemas que usam hoje (opcional)', '<input id="psis" type="text" placeholder="Ex.: planilhas, ERP X, WhatsApp" />'),
 fld('pusr', 'Quantas pessoas vão usar?', f'<select id="pusr"><option value="">Prefiro não informar</option>{opts(USERS)}</select>'),
 fld('ppri', 'Prioridade', f'<select id="ppri"><option value="">Selecione</option>{opts(PRIO)}</select>'),
 fld('pnome', 'Seu nome', '<input id="pnome" type="text" required autocomplete="name" />'),
 fld('pemp', 'Empresa (opcional)', '<input id="pemp" type="text" autocomplete="organization" />'),
 fld('pcont', 'WhatsApp ou e-mail para retorno', '<input id="pcont" type="text" required autocomplete="off" />'),
])
main = HERO('Apresente seu projeto', 'Conte o que você precisa e a gente prepara uma proposta', 'Preencha em 2 minutos. Você revisa o resumo antes de enviar. Não geramos preço automático: o valor depende do escopo e é definido após a conversa.', crumbs=[('Início', '/'), ('Apresente seu projeto', None)]) + f'''
<section class="sec-lav" style="padding:3.5rem 5% 5rem"><div class="section-inner" style="max-width:860px">
<form id="pf" class="tool-form" onsubmit="return false" novalidate>
<div class="pf-grid">{form}</div>
<div class="pf"><label style="display:flex;gap:.7rem;align-items:flex-start;font-weight:400;font-size:.88rem;color:var(--gray-600);line-height:1.6"><input type="checkbox" id="pok" required style="margin-top:.25rem;width:18px;height:18px;accent-color:#7C3AED" /> <span>Concordo com o tratamento dos dados informados para retorno e elaboração de proposta, conforme a <a href="/privacidade.html">Política de privacidade</a>. Não incluí dados sensíveis.</span></label></div>
<p id="perr" role="alert" style="color:#B91C1C;font-size:.88rem;font-weight:600" hidden></p>
<button type="submit" class="btn-primary" style="border:0;cursor:pointer;justify-self:start">Gerar resumo</button>
</form>
<div id="pres" class="result-box" role="status" aria-live="polite" hidden>
 <p class="kicker">Resumo do seu projeto</p>
 <pre id="ptxt" style="white-space:pre-wrap;font-family:inherit;line-height:1.8;margin-top:.8rem;color:#fff"></pre>
 <p class="note">Revise o texto. Ele só será enviado quando você clicar em um dos botões abaixo.</p>
 <div style="display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1rem">
  <a id="pwa" class="btn-primary" target="_blank" rel="noopener" href="#">Enviar pelo WhatsApp</a>
  <a id="pml" class="btn-ghost" href="#" style="color:#fff;border-color:rgba(255,255,255,.4)">Enviar por e-mail</a>
  <button type="button" id="pcp" class="btn-ghost" style="color:#fff;border-color:rgba(255,255,255,.4);background:transparent;cursor:pointer">Copiar texto</button>
 </div>
</div>
</div></section>
<style>.pf-grid{{display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}.pf label{{font-weight:700;color:var(--indigo);display:block;margin-bottom:.4rem}}
.pf input[type=text],.pf select,.pf textarea{{width:100%;padding:.75rem .9rem;border:1px solid #9CA3C7;border-radius:10px;font:inherit;background:#fff;color:#1E1B4B}}
.pf input:focus,.pf select:focus,.pf textarea:focus{{outline:2px solid #7C3AED;outline-offset:1px}}.pf textarea{{resize:vertical}}
html[data-theme=dark] .pf input[type=text],html[data-theme=dark] .pf select,html[data-theme=dark] .pf textarea{{background:#0F0D2A;color:#E6E4F5;border-color:#4B4F7A}}</style>
<script>
(function(){{
  var $=function(i){{return document.getElementById(i)}};
  function contato(v){{
    v=v.trim();if(!v)return{{err:'Informe um WhatsApp ou e-mail para retorno.'}};
    if(v.indexOf('@')>-1){{return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{{2,}}$/.test(v)?{{ok:v.toLowerCase()}}:{{err:'E-mail inválido. Use o formato nome@empresa.com.br.'}}}}
    var d=v.replace(/[\\s().\\-]/g,'');
    if(!/^\\+?\\d+$/.test(d))return{{err:'Contato inválido. Informe um e-mail ou um telefone com DDD, por exemplo (11) 98888-7777.'}};
    d=d.replace(/^\\+/,'');if(d.charAt(0)==='0'&&(d.length===11||d.length===12))d=d.slice(1);if(d.length>=12&&d.indexOf('55')===0)d=d.slice(2);
    if(d.length!==10&&d.length!==11)return{{err:'Telefone inválido. Informe DDD e número, por exemplo (11) 98888-7777. Com código do país: +55 11 98888-7777.'}};
    if(!/^[1-9][1-9]/.test(d))return{{err:'DDD inválido. Confira os dois primeiros dígitos.'}};
    if(d.length===11&&d.charAt(2)!=='9')return{{err:'Celular inválido: com 11 dígitos, o número deve começar com 9 depois do DDD.'}};
    if(d.length===10&&!/[2-5]/.test(d.charAt(2)))return{{err:'Telefone fixo inválido. Confira o número.'}};
    var n=d.slice(2);return{{ok:'('+d.slice(0,2)+') '+n.slice(0,n.length-4)+'-'+n.slice(-4)}};
  }}
  function bad(id,msg){{var e=$('perr');e.hidden=false;e.textContent=msg;$(id).setAttribute('aria-invalid','true');$(id).focus();return false}}
  $('pf').addEventListener('submit',function(){{
    var err=$('perr');err.hidden=true;['pseg','pneed','pprob','pnome','pcont','pok'].forEach(function(i){{$(i).removeAttribute('aria-invalid')}});
    var labels={{pseg:'Selecione o segmento da empresa.',pneed:'Selecione o que você procura.',pprob:'Descreva o problema que quer resolver.',pnome:'Informe o seu nome.'}};
    var ids=['pseg','pneed','pprob','pnome'];
    for(var i=0;i<ids.length;i++){{if(!$(ids[i]).value.trim())return bad(ids[i],labels[ids[i]])}}
    var c=contato($('pcont').value);if(c.err)return bad('pcont',c.err);
    if(!$('pok').checked)return bad('pok','Marque o consentimento para continuar.');
    var L=[['Segmento',$('pseg').value],['Procura',$('pneed').value],['Problema',$('pprob').value.trim()],['Solução imaginada',$('psol').value.trim()],['Sistemas atuais',$('psis').value.trim()],['Usuários',$('pusr').value],['Prioridade',$('ppri').value],['Nome',$('pnome').value.trim()],['Empresa',$('pemp').value.trim()],['Contato',c.ok]];
    var t='Olá! Quero apresentar um projeto:\\n'+L.filter(function(x){{return x[1]}}).map(function(x){{return '- '+x[0]+': '+x[1]}}).join('\\n');
    $('ptxt').textContent=t;$('pres').hidden=false;
    $('pwa').href='https://wa.me/{PHONE}?text='+encodeURIComponent(t);
    $('pml').href='mailto:contato@nexusefbusiness.com.br?subject='+encodeURIComponent('Projeto: '+$('pseg').value)+'&body='+encodeURIComponent(t);
    $('pres').scrollIntoView({{behavior:'smooth',block:'nearest'}});
  }});
  $('pf').addEventListener('input',function(){{$('pres').hidden=true}});
  $('pcp').addEventListener('click',function(){{var b=this;if(navigator.clipboard)navigator.clipboard.writeText($('ptxt').textContent).then(function(){{b.textContent='Copiado';setTimeout(function(){{b.textContent='Copiar texto'}},1800)}})}});
}})();
</script>'''
wr('projeto.html', page('projeto.html', 'Apresente seu projeto | Nexus EF Business', 'Descreva sua necessidade em 2 minutos e receba uma proposta personalizada. Sem preço automático, sem compromisso.', main, crumbs=[('Início', '/'), ('Apresente seu projeto', None)]))

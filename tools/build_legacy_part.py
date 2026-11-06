# ---------------- diagnóstico
diag=HERO('Diagnóstico','Quanto o seu time perde com tarefas repetitivas?','Responda três perguntas e veja uma estimativa de horas e custo por mês que poderiam ser liberadas com automação.',crumbs=[('Início','/'),('Ferramentas','/ferramentas/'),('Diagnóstico',None)])+'''
<section class="sec-lav" style="padding:3.5rem 5% 5rem">
  <div class="section-inner" style="max-width:860px">
    <form id="diag" style="display:grid;gap:1.6rem;background:#fff;border:1px solid var(--gray-100);border-radius:16px;padding:2rem" onsubmit="return false">
      <div>
        <label for="pessoas" style="font-weight:700;color:var(--indigo)">Quantas pessoas fazem tarefas repetitivas?</label>
        <div style="display:flex;gap:1rem;align-items:center;margin-top:.5rem"><input type="range" id="pessoas" min="1" max="50" value="5" style="flex:1" aria-describedby="pessoasV"><output id="pessoasV" for="pessoas" style="min-width:4rem;font-weight:700;color:var(--purple)">5</output></div>
      </div>
      <div>
        <label for="horas" style="font-weight:700;color:var(--indigo)">Horas por semana, por pessoa, em planilhas, cópia de dados e relatórios manuais</label>
        <div style="display:flex;gap:1rem;align-items:center;margin-top:.5rem"><input type="range" id="horas" min="1" max="30" value="4" style="flex:1" aria-describedby="horasV"><output id="horasV" for="horas" style="min-width:4rem;font-weight:700;color:var(--purple)">4 h</output></div>
      </div>
      <div>
        <label for="custo" style="font-weight:700;color:var(--indigo)">Custo médio da hora de trabalho</label>
        <div style="display:flex;gap:1rem;align-items:center;margin-top:.5rem"><input type="range" id="custo" min="15" max="200" step="5" value="40" style="flex:1" aria-describedby="custoV"><output id="custoV" for="custo" style="min-width:4rem;font-weight:700;color:var(--purple)">R$ 40</output></div>
      </div>
    </form>

    <div id="resultado" role="status" aria-live="polite" style="margin-top:1.5rem;background:#1E1B4B;color:#fff;border-radius:16px;padding:2rem">
      <p style="font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#C4B5FD">Estimativa ilustrativa</p>
      <div style="display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin-top:1rem">
        <div><p style="font-size:.85rem;color:rgba(255,255,255,.7)">Horas gastas por mês</p><p id="rHoras" style="font-family:'Lora',serif;font-size:1.9rem;font-weight:700"></p></div>
        <div><p style="font-size:.85rem;color:rgba(255,255,255,.7)">Custo por mês</p><p id="rCusto" style="font-family:'Lora',serif;font-size:1.9rem;font-weight:700"></p></div>
        <div><p style="font-size:.85rem;color:rgba(255,255,255,.7)">Economia possível por ano</p><p id="rAno" style="font-family:'Lora',serif;font-size:1.9rem;font-weight:700;color:#C4B5FD"></p></div>
      </div>
      <p style="font-size:.78rem;color:rgba(255,255,255,.6);margin-top:1.2rem;line-height:1.7">Cálculo: horas por mês = pessoas x horas por semana x 4,33. A economia considera que cerca de metade desse tempo pode ser automatizada. É uma estimativa para ter uma ideia de ordem de grandeza. O valor real depende do seu processo, e confirmamos isso no diagnóstico.</p>
      <a id="rCta" href="#" target="_blank" rel="noopener" class="btn-primary" style="margin-top:1.4rem">Quero analisar o meu processo</a>
    </div>
  </div>
</section>
<script>
  (function(){
    var $=function(i){return document.getElementById(i)};
    var brl=function(n){return n.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0})};
    var num=function(n){return Math.round(n).toLocaleString('pt-BR')};
    var hr=function(n){return n<10?n.toLocaleString('pt-BR',{maximumFractionDigits:1}):num(n)};
    function calc(){
      var p=+$('pessoas').value,h=+$('horas').value,c=+$('custo').value;
      var horasMes=p*h*4.33,custoMes=horasMes*c,ano=custoMes*12*0.5;
      $('pessoasV').textContent=p;$('horasV').textContent=h+' h';$('custoV').textContent='R$ '+c;
      $('rHoras').textContent=hr(horasMes)+' h';$('rCusto').textContent=brl(custoMes);$('rAno').textContent=brl(ano);
      var t='Olá! Fiz o diagnóstico no site: '+p+' pessoas, '+h+' h por semana cada, R$ '+c+' por hora. A estimativa deu cerca de '+hr(horasMes)+' h e '+brl(custoMes)+' por mês. Quero analisar o meu processo.';
      $('rCta').href='https://wa.me/5511926461357?text='+encodeURIComponent(t);
    }
    ['pessoas','horas','custo'].forEach(function(i){$(i).addEventListener('input',calc)});
    calc();
  })();
</script>'''
wr('diagnostico.html',page('diagnostico.html','Diagnóstico de automação | Nexus EF Business','Estime quantas horas e quanto dinheiro o seu time perde com tarefas repetitivas e veja o potencial de automação.',diag,crumbs=[('Início','/'),('Ferramentas','/ferramentas/'),('Diagnóstico',None)]))

# ---------------- demo Platform
shots=[('np-dashboard','Dashboard em tempo real','Visão geral dos chamados, do SLA e da equipe em um só painel.'),
('np-chamados','Fila de chamados','Todos os chamados com prioridade, responsável e status.'),
('np-chamado-detalhe','Detalhe completo do chamado','Histórico, comentários, SLA e ativo vinculado.'),
('np-resolucao','Conformidade de SLA e tempo de resolução','Quanto tempo cada atendimento levou e se o prazo foi cumprido.'),
('np-sla-violados','SLA violados e em risco','Os chamados que precisam de atenção antes de estourar o prazo.'),
('np-sla-charts','Ranking de técnicos e SLA por categoria','Onde a equipe está indo bem e onde há gargalo.'),
('np-sla-report','Relatório de SLA','Cumprimento de SLA por período para mostrar resultado à gestão.'),
('np-heatmap','Horários de pico','Quando os chamados mais chegam, para dimensionar a equipe.'),
('np-relatorios','Relatórios em tempo real','Volume, tempo de resolução e satisfação consolidados.'),
('np-inventario','Inventário de ativos','Equipamentos com responsável, localização e garantia.'),
('np-ativo-detalhe','Detalhe do ativo','Histórico de uso e de chamados de cada equipamento.'),
('np-base-conhecimento','Base de conhecimento','Artigos e respostas prontas para reduzir chamados repetitivos.'),
('np-auditoria','Auditoria','Registro imutável de todas as ações na plataforma.')]
data=json.dumps([{'src':f'/img/{a}.webp','t':b,'d':c} for a,b,c in shots],ensure_ascii=False)
demo=HERO('Nexus Platform','Veja a plataforma por dentro',"Um passeio pelas telas do helpdesk e do inventário de TI. As imagens são da versão anterior, e a nova versão está em desenvolvimento.",crumbs=[('Início','/'),('Nexus Platform','/nexus-platform.html'),('Telas',None)])+'''
<section class="sec-lav" style="padding:3rem 5% 5rem">
  <div class="section-inner" style="max-width:1100px">
    <div style="background:#1E1B4B;border-radius:18px;padding:1.2rem">
      <img id="dImg" src="" alt="" style="width:100%;border-radius:10px;display:block" />
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-top:1.2rem;flex-wrap:wrap">
      <button type="button" id="dPrev" class="btn-ghost" style="background:#fff;color:var(--indigo);border:1px solid var(--gray-100);cursor:pointer">Anterior</button>
      <div style="flex:1;min-width:220px;text-align:center" role="status" aria-live="polite"><p id="dT" style="font-family:'Lora',serif;color:var(--indigo);font-size:1.15rem;font-weight:700"></p><p id="dD" style="font-size:.9rem;color:var(--gray-600);margin-top:.2rem"></p><p id="dN" style="font-size:.78rem;color:var(--gray-600);margin-top:.3rem"></p></div>
      <button type="button" id="dNext" class="btn-primary" style="border:0;cursor:pointer">Próxima</button>
    </div>
    <div style="text-align:center;margin-top:2.2rem"><a href="https://wa.me/5511926461357?text=Olá! Vi as telas do Nexus Platform e quero pedir acesso antecipado." target="_blank" rel="noopener" class="btn-primary">Pedir acesso antecipado</a> <a href="/nexus-platform.html" style="margin-left:1rem;color:var(--purple);font-weight:600">Ver detalhes do produto</a></div>
  </div>
</section>
<script>
  (function(){
    var S=__DATA__,i=0,$=function(x){return document.getElementById(x)};
    function show(n){i=(n+S.length)%S.length;var s=S[i];$('dImg').src=s.src;$('dImg').alt=s.t;$('dT').textContent=s.t;$('dD').textContent=s.d;$('dN').textContent=(i+1)+' de '+S.length}
    $('dPrev').addEventListener('click',function(){show(i-1)});
    $('dNext').addEventListener('click',function(){show(i+1)});
    document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)});
    show(0);
  })();
</script>'''.replace('__DATA__',data)
wr('demo-platform.html',page('demo-platform.html','Veja o Nexus Platform por dentro | Nexus EF Business','Passeio pelas telas do Nexus Platform: chamados, SLA, inventário, relatórios, base de conhecimento e auditoria.',demo,crumbs=[('Início','/'),('Nexus Platform','/nexus-platform.html'),('Telas',None)]))


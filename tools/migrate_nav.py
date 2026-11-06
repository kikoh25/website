import re
ROOT='/home/claude/website/'
CSS='''    .nav-toggle{display:none;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.28);border-radius:10px;width:44px;height:44px;cursor:pointer;align-items:center;justify-content:center;flex-direction:column;gap:5px;padding:0}
    .nav-toggle span{display:block;width:20px;height:2px;background:#fff;border-radius:2px;transition:transform .2s,opacity .2s}
    nav.open .nav-toggle span:nth-child(1){transform:translateY(7px) rotate(45deg)}
    nav.open .nav-toggle span:nth-child(2){opacity:0}
    nav.open .nav-toggle span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
    @media (max-width:768px){
      .nav-toggle{display:flex}
      nav .nav-links{display:none!important}
      nav.open{background:#12102F!important}
      nav.open .nav-links{display:flex!important;flex-direction:column;align-items:stretch;gap:0;position:absolute;top:100%;left:0;right:0;background:#12102F;padding:.4rem 5% 1.4rem;border-bottom:1px solid rgba(255,255,255,.12);margin:0;list-style:none;max-height:calc(100vh - 70px);overflow:auto}
      nav.open .nav-links li{border-bottom:1px solid rgba(255,255,255,.08)}
      nav.open .nav-links a{display:block;padding:.95rem 0;font-size:1rem;color:#fff}
      nav.open .nav-links a.nav-cta{display:block;margin-top:1rem;text-align:center;padding:.9rem 1rem;border-bottom:0}
    }
  </style>'''
BTN='  <button type="button" class="nav-toggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu-principal"><span></span><span></span><span></span></button>\n</nav>'
JS='''<script>
(function(){
  var nav=document.querySelector('nav'),btn=document.querySelector('.nav-toggle');
  if(!nav||!btn)return;
  function set(o){nav.classList.toggle('open',o);btn.setAttribute('aria-expanded',o?'true':'false');btn.setAttribute('aria-label',o?'Fechar menu':'Abrir menu')}
  btn.addEventListener('click',function(){set(!nav.classList.contains('open'))});
  nav.querySelectorAll('.nav-links a').forEach(function(a){a.addEventListener('click',function(){set(false)})});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){set(false);btn.focus()}});
  document.addEventListener('click',function(e){if(!nav.contains(e.target))set(false)});
  window.addEventListener('resize',function(){if(window.innerWidth>768)set(false)});
})();
</script>
</body>'''
for f in ['index.html','servicos.html','privacidade.html','404.html','nexus-platform.html','nexus-contabil.html']:
    s=open(ROOT+f,encoding='utf-8').read()
    if 'nav-toggle' in s: continue
    s=s.replace('</style>',CSS,1)
    s=re.sub(r'(<ul class="nav-links">|<div class="nav-links">)',lambda m:m.group(1).replace('class="nav-links"','class="nav-links" id="menu-principal"'),s,count=1)
    i=s.index('</nav>'); s=s[:i]+BTN+s[i+6:]
    s=s.replace('</body>',JS,1)
    open(ROOT+f,'w',encoding='utf-8').write(s)
# step2: incluir JS nas páginas geradas
st=open('/tmp/claude-0/b/step2.py',encoding='utf-8').read()
if 'NAVJS' not in st:
    st=st.replace("def page(path","NAVJS=open('/tmp/claude-0/b/navjs.html',encoding='utf-8').read()\ndef page(path",1)
    st=st.replace("+fab()+'\\n</body>\\n</html>\\n'","+fab()+'\\n'+NAVJS+'\\n</html>\\n'",1)
    open('/tmp/claude-0/b/step2.py','w',encoding='utf-8').write(st)
open('/tmp/claude-0/b/navjs.html','w',encoding='utf-8').write(JS)

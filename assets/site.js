/* Recursos compartilhados: menu mobile, tema, contadores, popup de saída, busca do blog e PWA. */
(function () {
  'use strict';
  var d = document, w = window;
  var EN = (d.documentElement.lang || '').toLowerCase().indexOf('en') === 0;
  function ls(get, k, v) {
    try { return get ? localStorage.getItem(k) : localStorage.setItem(k, v); } catch (e) { return null; }
  }
  function ss(get, k, v) {
    try { return get ? sessionStorage.getItem(k) : sessionStorage.setItem(k, v); } catch (e) { return null; }
  }

  /* ---------- Menu mobile ---------- */
  var nav = d.querySelector('nav'), btn = d.querySelector('.nav-toggle');
  if (nav && btn) {
    var openLabel = EN ? 'Open menu' : 'Abrir menu', closeLabel = EN ? 'Close menu' : 'Fechar menu';
    var setNav = function (o) {
      nav.classList.toggle('open', o);
      btn.setAttribute('aria-expanded', o ? 'true' : 'false');
      btn.setAttribute('aria-label', o ? closeLabel : openLabel);
    };
    btn.addEventListener('click', function () { setNav(!nav.classList.contains('open')); });
    nav.querySelectorAll('.nav-links a').forEach(function (a) { a.addEventListener('click', function () { setNav(false); }); });
    d.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setNav(false); btn.focus(); }
    });
    d.addEventListener('click', function (e) { if (!nav.contains(e.target)) setNav(false); });
    w.addEventListener('resize', function () { if (w.innerWidth > 768) setNav(false); });
  }

  /* ---------- Tema claro/escuro ---------- */
  var root = d.documentElement;
  function syncTheme() {
    var dark = root.getAttribute('data-theme') === 'dark';
    d.querySelectorAll('.theme-toggle').forEach(function (b) {
      b.setAttribute('aria-pressed', dark ? 'true' : 'false');
      b.setAttribute('aria-label', EN ? (dark ? 'Switch to light theme' : 'Switch to dark theme') : (dark ? 'Mudar para tema claro' : 'Mudar para tema escuro'));
    });
    var m = d.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', '#1E1B4B');
  }
  d.querySelectorAll('.theme-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var dark = root.getAttribute('data-theme') === 'dark';
      if (dark) root.removeAttribute('data-theme'); else root.setAttribute('data-theme', 'dark');
      ls(false, 'theme', dark ? 'light' : 'dark');
      syncTheme();
    });
  });
  syncTheme();

  /* ---------- Contadores ---------- */
  var counters = d.querySelectorAll('[data-count]');
  if (counters.length) {
    var reduce = w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fmt = function (n) { return Math.round(n).toLocaleString(EN ? 'en-US' : 'pt-BR'); };
    var run = function (el) {
      var end = parseFloat(el.getAttribute('data-count')), suf = el.getAttribute('data-suffix') || '';
      if (reduce || !('requestAnimationFrame' in w)) { el.textContent = fmt(end) + suf; return; }
      var t0 = null, dur = 1400;
      var step = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(end * e) + suf;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if ('IntersectionObserver' in w) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting) { run(en.target); io.unobserve(en.target); } });
      }, { threshold: .4 });
      counters.forEach(function (c) { io.observe(c); });
    } else { counters.forEach(run); }
  }

  /* ---------- Barra de leitura em artigos ---------- */
  var art = d.querySelector('.article');
  if (art) {
    var bar = d.createElement('div');
    bar.className = 'read-progress';
    bar.setAttribute('aria-hidden', 'true');
    d.body.appendChild(bar);
    var upd = function () {
      var r = art.getBoundingClientRect(), total = r.height - w.innerHeight * .6;
      var p = total > 0 ? Math.min(1, Math.max(0, (-r.top + w.innerHeight * .2) / total)) : 0;
      bar.style.width = (p * 100) + '%';
    };
    w.addEventListener('scroll', upd, { passive: true });
    upd();
  }

  /* ---------- Compartilhar / copiar link ---------- */
  d.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = w.location.href.split('#')[0], old = b.textContent;
      var done = function (ok) {
        b.textContent = ok ? (EN ? 'Link copied' : 'Link copiado') : (EN ? 'Copy failed' : 'Não foi possível copiar');
        setTimeout(function () { b.textContent = old; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); });
      else done(false);
    });
  });

  /* ---------- Busca e filtro do blog ---------- */
  var blog = d.querySelector('[data-blog]');
  if (blog) {
    var q = d.getElementById('blogSearch'), cards = [].slice.call(blog.querySelectorAll('[data-tags]'));
    var tagBtns = [].slice.call(d.querySelectorAll('.tag-btn')), none = d.getElementById('noResults'), live = d.getElementById('blogCount');
    var tag = 'all';
    var norm = function (s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
    var apply = function () {
      var term = norm(q ? q.value : ''), shown = 0;
      cards.forEach(function (c) {
        var okTag = tag === 'all' || c.getAttribute('data-tags').split(',').indexOf(tag) > -1;
        var okTerm = !term || norm(c.getAttribute('data-title') + ' ' + c.textContent).indexOf(term) > -1;
        var show = okTag && okTerm;
        c.style.display = show ? '' : 'none';
        if (show) shown++;
      });
      if (none) none.style.display = shown ? 'none' : 'block';
      if (live) live.textContent = shown + (shown === 1 ? ' artigo' : ' artigos');
    };
    if (q) q.addEventListener('input', apply);
    tagBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        tag = b.getAttribute('data-tag');
        tagBtns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        apply();
      });
    });
    apply();
  }

  /* ---------- Popup de saída (só computador, uma vez por sessão) ---------- */
  if (d.body.hasAttribute('data-exit') && w.matchMedia && w.matchMedia('(hover: hover) and (pointer: fine)').matches && !ss(true, 'exitShown')) {
    var armed = false, last = null;
    setTimeout(function () { armed = true; }, 9000);
    var ov = d.createElement('div');
    ov.className = 'exit-ov';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-modal', 'true');
    ov.setAttribute('aria-labelledby', 'exitT');
    ov.innerHTML = '<div class="exit-card"><button type="button" class="exit-x" aria-label="' + (EN ? 'Close' : 'Fechar') + '">×</button>' +
      '<h2 id="exitT">' + (EN ? 'Before you go: how much time does your team lose?' : 'Antes de ir: quanto o seu time perde com tarefas repetitivas?') + '</h2>' +
      '<p>' + (EN ? 'Take the 1-minute diagnostic and get an estimate of hours and cost.' : 'Faça o diagnóstico em 1 minuto e veja uma estimativa de horas e custo por mês.') + '</p>' +
      '<a class="btn-primary" href="/diagnostico.html">' + (EN ? 'Take the diagnostic' : 'Fazer o diagnóstico') + '</a></div>';
    d.body.appendChild(ov);
    var close = function () { ov.classList.remove('show'); if (last && last.focus) last.focus(); };
    ov.querySelector('.exit-x').addEventListener('click', close);
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    d.addEventListener('keydown', function (e) {
      if (!ov.classList.contains('show')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'Tab') {
        var f = ov.querySelectorAll('button,a'), a = f[0], z = f[f.length - 1];
        if (e.shiftKey && d.activeElement === a) { e.preventDefault(); z.focus(); }
        else if (!e.shiftKey && d.activeElement === z) { e.preventDefault(); a.focus(); }
      }
    });
    d.addEventListener('mouseout', function (e) {
      if (!armed || e.relatedTarget || e.clientY > 0 || ov.classList.contains('show')) return;
      last = d.activeElement;
      ss(false, 'exitShown', '1');
      ov.classList.add('show');
      ov.querySelector('.exit-x').focus();
    });
  }

  /* ---------- PWA: só o aviso offline, sem cache de conteúdo ---------- */
  if ('serviceWorker' in navigator && (w.location.protocol === 'https:' || w.location.hostname === 'localhost' || w.location.hostname === '127.0.0.1')) {
    w.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });
  }
})();

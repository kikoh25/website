// Service worker mínimo: só mostra a página offline quando a navegação falha. Não guarda conteúdo.
const OFF='offline-v1';
self.addEventListener('install',e=>{e.waitUntil(caches.open(OFF).then(c=>c.add('/offline.html')).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==OFF).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).catch(()=>caches.match('/offline.html')))}});

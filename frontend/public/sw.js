// frontend/public/sw.js
// Service Worker do Portal TRK (PWA).
//
// Estratégia (corrige o problema de "deploy novo, app antigo"):
//   - Navegação/HTML  -> NETWORK-FIRST: sempre busca o index.html mais novo;
//                         só usa cache se estiver offline.
//   - Assets hasheados-> CACHE-FIRST: nome do arquivo muda a cada build
//                         (index-XXXX.js), então o cache nunca fica obsoleto.
//   - API GET         -> NETWORK-FIRST com fallback ao cache (offline).
//
// IMPORTANTE: ao mudar a estratégia, suba o CACHE_NAME para invalidar o antigo.

const CACHE_NAME = 'portal-trk-v3';
const OFFLINE_URL = '/offline.html';

const STATIC_ASSETS = [
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  OFFLINE_URL,
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    ).then(() => self.clients.claim())
  );
});

// Permite que a página force a ativação imediata do SW novo
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  // 1) Navegação (HTML) -> network-first, com fallback offline
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE_NAME).then((c) => c.put('/index.html', copy));
          return resp;
        })
        .catch(() =>
          caches.match('/index.html').then((r) => r || caches.match(OFFLINE_URL))
        )
    );
    return;
  }

  // 2) API GET -> network-first, fallback ao cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE_NAME).then((c) => c.put(request, copy));
          return resp;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // 3) Assets estáticos (hasheados) -> cache-first
  event.respondWith(
    caches.match(request).then((cached) =>
      cached ||
      fetch(request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE_NAME).then((c) => c.put(request, copy));
        return resp;
      }).catch(() => caches.match(OFFLINE_URL))
    )
  );
});

// ─── Web Push ───
self.addEventListener('push', (event) => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      data: data.url || '/',
      vibrate: [100, 50, 100],
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const urlToOpen = new URL(event.notification.data, self.location.origin).href;
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((wins) => {
      for (const client of wins) {
        if (client.url === urlToOpen && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(urlToOpen);
    })
  );
});

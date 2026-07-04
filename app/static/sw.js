// Freehold — service worker. Caches the app shell so the app installs and opens
// even offline. Served from / (via a route) so its scope is the whole app.
const CACHE = 'freehold-v2';

// Paths the SW must NEVER handle: Keycloak's hosted pages (login, register,
// password-reset action links), the OIDC round-trip, and MinIO media. Caching or
// offline-falling-back over these would shadow the real auth flow with our app
// shell — which is exactly what makes a reset link land on "You're offline".
const BYPASS = ['/realms/', '/resources/', '/admin/', '/js/', '/auth/', '/media/'];
const SHELL = [
  '/',
  '/static/app.css',
  '/static/favicon.svg',
  '/static/manifest.webmanifest',
  '/static/offline.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Auth (Keycloak) + media: hands off to the network, never the SW. Otherwise a
  // flaky moment turns a real login/reset page into our offline shell.
  if (BYPASS.some((p) => url.pathname.startsWith(p))) return;

  // Static assets: cache-first (fast, offline-safe).
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(caches.match(req).then((r) => r || fetch(req)));
    return;
  }

  // Pages: network-first, fall back to cache, then the offline page.
  event.respondWith(
    fetch(req).catch(() =>
      caches.match(req).then((r) => r || caches.match('/static/offline.html'))
    )
  );
});

const CACHE_NAME = 'pwa-login-db-v1';
const URLS_TO_CACHE = [
  '/',
  '/login',
  '/signup',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(URLS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request);
    })
  );
});
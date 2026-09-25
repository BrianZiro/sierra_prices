const CACHE_NAME = 'sierra-prices-v2';
const urlsToCache = [
    '/',
    '/login/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/icons/logo.png',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css'
];

// Install – pre-cache core assets
self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
            .catch(err => console.warn('Pre-cache failed:', err))
    );
});

// Activate – clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch – network-first for HTML, cache-first for static
self.addEventListener('fetch', event => {
    const req = event.request;
    if (req.method !== 'GET') return;

    // Never cache admin or Django admin URLs
    if (req.url.includes('/admin/')) return;

    const isHTML = req.headers.get('accept')?.includes('text/html');

    if (isHTML) {
        // Network-first for pages
        event.respondWith(
            fetch(req)
                .then(res => {
                    const copy = res.clone();
                    caches.open(CACHE_NAME).then(c => c.put(req, copy));
                    return res;
                })
                .catch(() => caches.match(req).then(r => r || caches.match('/')))
        );
    } else {
        // Cache-first for static assets
        event.respondWith(
            caches.match(req).then(cached => cached || fetch(req).then(res => {
                const copy = res.clone();
                caches.open(CACHE_NAME).then(c => c.put(req, copy));
                return res;
            }))
        );
    }
});
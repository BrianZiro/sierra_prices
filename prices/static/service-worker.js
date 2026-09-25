const CACHE_NAME = 'sierra-prices-v3';
const RUNTIME_CACHE = 'sierra-runtime-v3';

const PRECACHE_URLS = [
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

// Install – pre-cache
self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .catch(err => console.warn('Pre-cache failed:', err))
    );
});

// Activate – clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_NAME && k !== RUNTIME_CACHE)
                    .map(k => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch strategies
self.addEventListener('fetch', event => {
    const req = event.request;

    // Only handle GET requests
    if (req.method !== 'GET') return;

    // Only handle http(s) — skip chrome-extension://, moz-extension://, data:, etc.
    if (!req.url.startsWith('http://') && !req.url.startsWith('https://')) return;

    const url = new URL(req.url);

    // Never cache Django admin
    if (url.pathname.startsWith('/admin/')) return;

    // API: network-first, fallback to cache
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(req)
                .then(res => {
                    // Only cache successful responses
                    if (res && res.status === 200) {
                        const copy = res.clone();
                        caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
                    }
                    return res;
                })
                .catch(() => caches.match(req))
        );
        return;
    }

    // HTML pages: network-first, fallback to cache, then to '/'
    if (req.headers.get('accept')?.includes('text/html')) {
        event.respondWith(
            fetch(req)
                .then(res => {
                    if (res && res.status === 200) {
                        const copy = res.clone();
                        caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
                    }
                    return res;
                })
                .catch(() =>
                    caches.match(req).then(r => r || caches.match('/'))
                )
        );
        return;
    }

    // Static assets: cache-first, then network
    event.respondWith(
        caches.match(req).then(cached => {
            if (cached) return cached;
            return fetch(req).then(res => {
                // Only cache valid, same-origin or CDN http(s) responses
                if (res && res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
                    const copy = res.clone();
                    caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
                }
                return res;
            });
        })
    );
});
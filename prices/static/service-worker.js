const CACHE_NAME = 'sierra-prices-v2';

const PRECACHE_URLS = [
    '/',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/icons/favicon-32x32.png',
    '/static/icons/favicon-16x16.png',
    '/static/icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys =>
                Promise.all(
                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => caches.delete(key))
                )
            )
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const req = event.request;

    // Only handle HTTP/HTTPS requests.
    // Chrome extension requests cannot be stored in Cache API.
    if (req.url.startsWith('chrome-extension://')) {
        return;
    }

    if (!req.url.startsWith('http://') && !req.url.startsWith('https://')) {
        return;
    }

    const isHTML = req.mode === 'navigate' ||
                   req.headers.get('accept')?.includes('text/html');

    if (isHTML) {
        // Network-first for pages
        event.respondWith(
            fetch(req)
                .then(res => {
                    if (res.ok) {
                        const copy = res.clone();
                        caches.open(CACHE_NAME).then(c => c.put(req, copy));
                    }
                    return res;
                })
                .catch(() =>
                    caches.match(req).then(r => r || caches.match('/'))
                )
        );
    } else {
        // Cache-first for static assets
        event.respondWith(
            caches.match(req).then(cached =>
                cached || fetch(req).then(res => {
                    if (res.ok) {
                        const copy = res.clone();
                        caches.open(CACHE_NAME).then(c => c.put(req, copy));
                    }
                    return res;
                })
            )
        );
    }
});
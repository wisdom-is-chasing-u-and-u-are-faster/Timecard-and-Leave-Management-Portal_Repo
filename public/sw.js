// PWA Service Worker for Offline Punch Ingestion
const CACHE_NAME = 'timecard-portal-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/pages/login.html',
    '/pages/employee_dashboard.html',
    '/pages/my_timecard.html',
    '/pages/my_leave.html',
    '/pages/supervisor_dashboard.html',
    '/pages/team_approvals.html',
    '/js/api.js',
    '/css/style.css'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE).catch(() => {});
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (event.request.method === 'GET' && !event.request.url.includes('/api/')) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                return cached || fetch(event.request).catch(() => caches.match('/pages/employee_dashboard.html'));
            })
        );
    }
});

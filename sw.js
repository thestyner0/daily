// 네트워크 우선, 실패하면 캐시 (오프라인에서도 마지막 버전과 주차 기록 확인 가능)
const C = 'daily-v1';
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  const k = u.origin + u.pathname;
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(C).then(c => c.put(k, cp)); }
    return r;
  }).catch(() => caches.match(k)));
});

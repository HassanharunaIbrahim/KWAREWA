{% load static %}// KWAREWA service worker: shows an offline page when the network is down
// and keeps copies of static files (CSS, icons) for faster loading.
// Pages are never cached, so nobody sees another person's account details.
const CACHE = "kwarewa-v1";
const OFFLINE_URL = "{% url 'offline' %}";
const PRECACHE = [
  OFFLINE_URL,
  "{% static 'marketplace/style.css' %}",
  "{% static 'marketplace/icons/icon-192.png' %}",
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(PRECACHE);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (key) { return key !== CACHE; })
            .map(function (key) { return caches.delete(key); })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  const request = event.request;
  if (request.method !== "GET") { return; }
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) { return; }

  // Pages: always ask the network; show the offline page if it fails.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(function () { return caches.match(OFFLINE_URL); })
    );
    return;
  }

  // Static files: answer from the cache, and refresh the copy in the background.
  if (url.pathname.indexOf("/static/") === 0) {
    event.respondWith(
      caches.open(CACHE).then(function (cache) {
        return cache.match(request).then(function (cached) {
          const fresh = fetch(request).then(function (response) {
            if (response.ok) { cache.put(request, response.clone()); }
            return response;
          }).catch(function () { return cached; });
          return cached || fresh;
        });
      })
    );
  }
});

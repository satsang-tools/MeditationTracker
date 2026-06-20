/* Sitting — service worker. Bump CACHE when shipping changes so clients refresh. */
var CACHE = "sitting-v15";
var SHELL = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png",
  "icons/apple-touch-icon.png"
];

self.addEventListener("install", function(event){
  event.waitUntil(
    caches.open(CACHE).then(function(cache){ return cache.addAll(SHELL); })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function(event){
  event.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.map(function(k){
        if(k !== CACHE) return caches.delete(k);
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

// Cache-first with network fallback. The app has no external runtime deps, so this
// gives instant, fully-offline loads; new content arrives after a CACHE version bump.
self.addEventListener("fetch", function(event){
  if(event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then(function(hit){
      if(hit) return hit;
      return fetch(event.request).then(function(resp){
        var copy = resp.clone();
        caches.open(CACHE).then(function(cache){ cache.put(event.request, copy); }).catch(function(){});
        return resp;
      }).catch(function(){
        // offline and uncached: for navigations, fall back to the app shell
        if(event.request.mode === "navigate") return caches.match("index.html");
      });
    })
  );
});

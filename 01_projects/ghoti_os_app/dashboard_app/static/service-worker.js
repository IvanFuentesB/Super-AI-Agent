"use strict";

const APP_VERSION = "2026.08.01.4";
const CACHE_NAME = `ghoti-static-shell-${APP_VERSION}`;
const STATIC_SHELL = [
  "/",
  "/static/styles.css",
  "/static/app.js",
  "/assets/ghoti_fish_original.png",
  "/manifest.webmanifest",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/apple-touch-icon.png",
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
  )));
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(request, { cache: "no-store" }));
    return;
  }
  if (!STATIC_SHELL.includes(url.pathname)) return;
  event.respondWith(caches.match(request, { ignoreSearch: true }).then(cached => cached || fetch(request)));
});

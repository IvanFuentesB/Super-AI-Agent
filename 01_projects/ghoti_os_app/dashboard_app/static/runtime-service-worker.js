"use strict";

// Operator state must come from the active release, never an offline app shell.
// This replaces the legacy worker at the same URL without touching other caches.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith("ghoti-static-shell-"))
      .map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
// No fetch handler: normal requests use the backend's no-store responses.

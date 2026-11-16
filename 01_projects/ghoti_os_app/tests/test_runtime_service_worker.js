"use strict";
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

test("deployed worker retires only the old shell and takes over", async () => {
  const handlers = new Map();
  const deleted = [];
  let claimed = false;
  let skipped = false;
  vm.runInNewContext(readFileSync(path.join(__dirname, "../dashboard_app/static/runtime-service-worker.js"), "utf8"), {
    self: {
      addEventListener: (name, handler) => handlers.set(name, handler),
      skipWaiting: () => { skipped = true; },
      clients: { claim: async () => { claimed = true; } },
    },
    caches: {
      keys: async () => ["ghoti-static-shell-old", "ghoti-static-shell-new", "unrelated-user-cache"],
      delete: async key => { deleted.push(key); return true; },
    },
  });
  handlers.get("install")();
  let activated;
  handlers.get("activate")({ waitUntil: promise => { activated = promise; } });
  await activated;
  assert.equal(skipped, true);
  assert.equal(claimed, true);
  assert.deepEqual(deleted, ["ghoti-static-shell-old", "ghoti-static-shell-new"]);
  assert.equal(handlers.has("fetch"), false, "no cached fallback may impersonate the live runtime");
});

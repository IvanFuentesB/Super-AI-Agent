"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const file = path.join(__dirname, "../dashboard_app/static/local-session.js");
(async () => {
  assert.ok(fs.existsSync(file), "the app cannot exchange a launcher-bound session yet");
  const {LocalConnection} = require(file);
  const requests = [], replacements = [];
  const location = {href: "http://127.0.0.1:8765/#ghoti_local=fixture-ticket", hostname: "127.0.0.1", protocol: "http:"};
  const local = new LocalConnection({location, history: {replaceState: (...args) => replacements.push(args)},
    fetch: async (url, options) => {
      assert.equal(replacements.length, 1, "remove the transient ticket before network work");
      requests.push([url, options]);
      return {ok: true, json: async () => ({authenticated: true, csrf_token: "fixture-csrf"})};
    }});
  await local.bootstrap();
  assert.equal(local.authenticated, true);
  assert.equal(replacements[0][2], "/#chat");
  await local.request("/api/runtime/computer/tasks", {method: "POST", body: {request_id: "fixture"}});
  assert.equal(requests[1][1].headers["X-Ghoti-CSRF"], "fixture-csrf");
  assert.equal(requests[1][1].credentials, "same-origin");
  await assert.rejects(local.request("https://example.invalid/collect", {method: "POST"}));
  const remote = new LocalConnection({location: {href: "https://example.invalid/", hostname: "example.invalid", protocol: "https:"}, fetch: () => {throw Error("must not connect");}});
  await remote.bootstrap();
  assert.equal(remote.authenticated, false);
  console.log("local session browser boundary: passed (fixture HTTP only)");
})().catch(error => { console.error(error); process.exitCode = 1; });

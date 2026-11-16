"use strict";
// An unchanged Paperclip refresh must not rewrite the board's state attribute. Synthetic DOM/API only.
// STATIC_ROOT may point at another static directory (used to run the same file against a baseline).
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = process.env.STATIC_ROOT || path.join(__dirname, "../dashboard_app/static");

class Element {
  constructor(tag = "div") { this.tagName = tag; this.children = []; this.handlers = {}; this.listeners = {}; this.dataset = {}; this.value = ""; this.hidden = false; this.disabled = false; this._text = ""; this.attributes = {}; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(" "); }
  set innerHTML(_) { throw new Error("Unsafe DOM sink"); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute(k, v) { this.attributes[k] = v; }
  addEventListener(k, f) {
    (this.listeners[k] ||= []).push(f);
    this.handlers[k] = (...args) => { const out = this.listeners[k].map(fn => fn(...args)); return out.length === 1 ? out[0] : Promise.all(out); };
  }
  focus() {}
}
const settle = async () => { for (let i = 0; i < 4; i += 1) await new Promise(resolve => setImmediate(resolve)); };

async function shell(paperclip, options) {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
  // Count every write to the Paperclip state attribute, including same-value writes.
  const writes = [];
  const target = elements["daily-paperclip"];
  target.dataset = new Proxy({}, {set(obj, key, value) { if (key === "state") writes.push(value); obj[key] = value; return true; }});
  const data = {schema: "ghoti_deployed_runtime/1", deployment: {status: "NOT_INSTALLED"}, live_workers_running: 0,
    safe_operations: ["capability_lookup"], safe_workflows: [], jobs: [], memory: {obsidian_reference_count: 0, native_run_count: 0},
    learning: {status: "NOT_VERIFIED"}, computer_use: {status: "NOT_VERIFIED"}, observations: {
      scope: "Fixture observation window", verification_scope: "Transport is not task correctness", memory_status: "written", capabilities: [], receipts: []},
    integrations: paperclip ? {paperclip} : undefined};
  const ok = body => ({ok: true, json: async () => body});
  const context = {document: {getElementById: id => elements[id], createElement: tag => new Element(tag), querySelectorAll: () => [], addEventListener() {}, hidden: false},
    window: {addEventListener() {}}, navigator: {}, location: {hostname: "example.invalid"},
    fetch: async (url, init) => {
      if (url === "/api/runtime/state") { if (options.stateFails) throw new Error("fixture offline"); return ok(data); }
      if (url === "/api/runtime/chat" && init?.method !== "POST") return ok({schema: "ghoti_chat_state/1", available: true, csrf_token: "fixture-csrf", reasoning_effort: "max", models: [{id: "openai-codex:gpt-6-astra"}], sessions: []});
      if (url.includes("/events")) return {ok: false, status: 500};
      return {ok: false, status: 403};
    },
    setTimeout() {}, clearTimeout() {}, AbortSignal, TextEncoder, Date, console,
    crypto: {randomUUID: (() => { let n = 0; return () => `fixture-id-${++n}`; })()}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(root, "chat.js"), "utf8"), context);
  vm.runInContext(fs.readFileSync(path.join(root, "daily.js"), "utf8"), context);
  await settle();
  return {elements, writes};
}
const refresh = async e => { await e["daily-refresh"].handlers.click(); await settle(); };
const board = (status, pending_approvals) => ({schema: "ghoti_paperclip_status/1", status, pending_approvals});

for (const [label, paperclip, state] of [
  ["a reported board", board("RUNNING", 2), "permission"],
  ["no board report", null, "unconfirmed"],
]) {
  test(`an identical refresh with ${label} does not rewrite the Paperclip state`, async () => {
    const options = {};
    const {elements, writes} = await shell(paperclip, options);
    assert.equal(elements["daily-paperclip"].dataset.state, state, "precondition");
    const before = writes.length;
    const text = elements["daily-paperclip"].textContent;
    await refresh(elements);
    await refresh(elements);
    assert.equal(writes.length, before, `no further writes, saw ${JSON.stringify(writes.slice(before))}`);
    assert.equal(elements["daily-paperclip"].textContent, text);
  });
}

test("repeated failed refreshes write the unavailable state once, and a change is still written", async () => {
  const options = {};
  const {elements, writes} = await shell(board("STOPPED", 0), options);
  assert.equal(elements["daily-paperclip"].dataset.state, "attention");
  options.stateFails = true;
  const before = writes.length;
  await refresh(elements);
  await refresh(elements);
  assert.deepEqual(writes.slice(before), ["unavailable"]);
});

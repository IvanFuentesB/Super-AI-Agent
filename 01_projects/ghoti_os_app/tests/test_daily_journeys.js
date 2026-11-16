"use strict";
// Spec-first journey tests for the daily shell. Synthetic DOM/API responses only; never used by the served app.
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.join(__dirname, "../dashboard_app/static");
const MODEL = "openai-codex:gpt-6-astra";
class Element {
  constructor(tag = "div") { this.tagName = tag; this.children = []; this.handlers = {}; this.listeners = {}; this.dataset = {}; this.value = ""; this.hidden = false; this.disabled = false; this._text = ""; this.attributes = {}; this.attributeCalls = []; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(" "); }
  set innerHTML(_) { throw new Error("Unsafe DOM sink"); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute(k, v) { this.attributeCalls.push(k); this.attributes[k] = v; }
  // Every listener runs; handlers[k] is a dispatcher so tests can call it like the browser would.
  addEventListener(k, f) {
    (this.listeners[k] ||= []).push(f);
    this.handlers[k] = (...args) => { const out = this.listeners[k].map(fn => fn(...args)); return out.length === 1 ? out[0] : Promise.all(out); };
  }
  requestSubmit() { return this.handlers.submit?.({preventDefault() {}}); }
  focus() {}
}
// options.setup(data) edits runtime fixture state before first load; options.stateFails makes the runtime request reject.
async function shell(options = {}) {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
  const calls = [];
  const data = {schema: "ghoti_deployed_runtime/1", deployment: {status: "NOT_INSTALLED"}, live_workers_running: 0,
    safe_operations: ["capability_lookup"], safe_workflows: [], jobs: [], memory: {obsidian_reference_count: 0, native_run_count: 0},
    learning: {status: "NOT_VERIFIED"}, computer_use: {status: "NOT_VERIFIED"}, observations: {
      scope: "Fixture observation window", verification_scope: "Transport is not task correctness", memory_status: "written",
      capabilities: [], receipts: []}};
  if (options.setup) options.setup(data);
  const chat = {eventsFail: false, sessionId: "fixture-session"};
  const timers = [];
  const documentHandlers = {};
  const ok = body => ({ok: true, json: async () => body});
  const context = {document: {getElementById: id => elements[id], createElement: tag => new Element(tag),
      querySelectorAll: () => [], addEventListener: (k, f) => { (documentHandlers[k] ||= []).push(f); }, hidden: false},
    window: {addEventListener: () => {}}, navigator: {}, location: {hostname: "example.invalid"},
    fetch: async (url, init) => {
      calls.push({url, options: init});
      if (url === "/api/runtime/state") { if (options.stateFails) throw new Error("fixture offline"); return ok(data); }
      const post = init?.method === "POST";
      if (url === "/api/runtime/chat" && !post) return ok({schema: "ghoti_chat_state/1", available: true, csrf_token: "fixture-csrf",
        reasoning_effort: "max", models: [{id: MODEL}], sessions: []});
      if (url === "/api/runtime/chat/sessions" && post) return ok({session_id: chat.sessionId, model_id: MODEL, reasoning_effort: "max", state: "idle"});
      if (url.endsWith("/prompt") && post) return ok({session_id: chat.sessionId, request_id: JSON.parse(init.body).request_id, state: "running"});
      if (url.endsWith("/cancel") && post) return ok({session_id: chat.sessionId, state: "idle"});
      if (url.includes("/events")) { if (chat.eventsFail) throw new Error("network down"); return {ok: false, status: 500}; }
      return {ok: false, status: 403};
    },
    setTimeout: f => {timers.push(f);}, clearTimeout: () => {}, AbortSignal, TextEncoder, Date, console,
    crypto: {randomUUID: (() => { let n = 0; return () => `fixture-id-${++n}`; })()}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(root, "chat.js"), "utf8"), context);
  vm.runInContext("globalThis.testClients=[]; const Base=GhotiChat.ChatClient; GhotiChat.ChatClient=class extends Base {constructor(options){super(options);testClients.push(this);}};", context);
  vm.runInContext(fs.readFileSync(path.join(root, "daily.js"), "utf8"), context);
  await settle();
  return {elements, context, calls, timers, data, chat, documentHandlers};
}
const settle = async () => { for (let i = 0; i < 4; i += 1) await new Promise(resolve => setImmediate(resolve)); };
const posts = (calls, suffix) => calls.filter(c => c.options?.method === "POST" && c.url.endsWith(suffix));
const chatGets = calls => calls.filter(c => c.url === "/api/runtime/chat" && !c.options?.method);
const refresh = async e => { await e["daily-refresh"].handlers.click(); await settle(); };
const refs = n => Array.from({length: n}, (_, i) => ({system: i % 2 ? "brain" : "obsidian", reason: `Reference note ${i}`}));
const setPhase = (context, phase) => { const client = context.testClients.at(-1); client.state.phase = phase; client.changed(); };

// A. Memory count
test("A memory count: total, singular, filtered, empty and unavailable", async () => {
  let s = await shell({setup: d => { d.memory.startup_references = refs(3); }});
  assert.equal(s.elements["daily-memory-count"].textContent, "3 references loaded");
  s.elements["daily-memory-search"].value = "note 1";
  s.elements["daily-memory-search"].handlers.input();
  assert.equal(s.elements["daily-memory-count"].textContent, "1 of 3 references match");
  s.elements["daily-memory-search"].value = "";
  s.elements["daily-memory-search"].handlers.input();
  assert.equal(s.elements["daily-memory-count"].textContent, "3 references loaded");
  s = await shell({setup: d => { d.memory.startup_references = refs(1); }});
  assert.equal(s.elements["daily-memory-count"].textContent, "1 reference loaded");
  s = await shell();
  assert.equal(s.elements["daily-memory-count"].textContent, "No references loaded.");
  s = await shell({stateFails: true});
  assert.equal(s.elements["daily-memory-count"].textContent, "Memory unavailable.");
});

// B. Job summary
test("B job summary buckets and ordering", async () => {
  const cases = [
    [[{state: "executing", running: true}, {state: "pending"}, {state: "failed"}, {state: "succeeded"}, {state: "succeeded"}], "1 running · 1 queued · 1 needs review · 2 completed"],
    [[{state: "created"}, {state: "pending"}, {state: "verifying", running: true}], "1 running · 2 queued"],
    [[{state: "failed"}, {state: "blocked"}, {state: "interrupted"}, {state: "executing", running: false}, {state: "verifying"}], "5 need review"],
    [[{state: "succeeded"}], "1 completed"],
    [[], ""],
  ];
  for (const [jobs, expected] of cases) {
    const {elements: e} = await shell({setup: d => { d.jobs = jobs.map(j => ({title: "Fixture", ...j})); }});
    assert.equal(e["daily-jobs-summary"].textContent, expected, JSON.stringify(jobs));
  }
});

// C. Queued rows
test("C queued job row is not shown as running", async () => {
  const {elements: e} = await shell({setup: d => { d.jobs = [{title: "Fixture", state: "pending"}]; }});
  const row = e["daily-jobs"].children[0];
  assert.match(row.textContent, /Queued · not started/);
  assert.equal(row.dataset.state, "queued");
});

// D. Navigation state labels
test("D projects and memory nav labels", async () => {
  let s = await shell({setup: d => { d.jobs = [{title: "Fixture", state: "executing", running: true}]; d.observations.memory_status = "MEMORY_STALE"; }});
  assert.equal(s.elements["daily-nav-projects-state"].textContent, "1 running");
  assert.equal(s.elements["daily-nav-memory-state"].textContent, "Needs attention");
  s = await shell();
  assert.equal(s.elements["daily-nav-projects-state"].textContent, "");
  assert.equal(s.elements["daily-nav-memory-state"].textContent, "");
});

test("D chat nav label and dataset.state follow chat phase", async () => {
  const expected = {permission: ["Needs approval", "permission"], running: ["Working", "running"], submitting: ["Working", "running"],
    creating: ["Working", "running"], syncing: ["Working", "running"], approving: ["Working", "running"], cancelling: ["Stopping", "cancelling"],
    disconnected: ["Connection lost", "disconnected"], unavailable: ["Unavailable", "unavailable"], ready: ["", ""], complete: ["", ""]};
  for (const [phase, [label, state]] of Object.entries(expected)) {
    const {elements: e, context} = await shell();
    context.testClients[0].state.sessionId = "fixture-session";
    setPhase(context, phase);
    assert.equal(e["daily-nav-chat-state"].textContent, label, phase);
    assert.equal(e["daily-nav-chat-state"].dataset.state, state, phase);
  }
});

// E. Chat dead end
test("E disconnected chat can start a new chat without resending the old prompt", async () => {
  const {elements: e, context, calls, chat} = await shell();
  assert.equal(context.testClients[0].state.phase, "ready");
  e["daily-prompt"].value = "fixture prompt";
  await e["daily-chat-form"].handlers.submit({preventDefault() {}});
  assert.equal(posts(calls, "/prompt").length, 1);
  assert.equal(context.testClients[0].state.phase, "running");
  chat.eventsFail = true;
  await context.testClients[0].poll();
  await settle();
  assert.equal(context.testClients[0].state.phase, "disconnected");
  assert.match(context.testClients[0].state.reason, /Safety cancellation|Worker reported idle/, "safety cancel settled");
  assert.equal(e["daily-new"].disabled, false);
  assert.match(e["daily-chat-state"].textContent, /Start a new chat/);
  assert.equal(e["daily-send"].disabled, true);
  const gets = chatGets(calls).length;
  await e["daily-new"].handlers.click();
  await settle();
  assert.equal(context.testClients.length, 2);
  assert.equal(chatGets(calls).length, gets + 1, "new client bootstraps");
  assert.equal(posts(calls, "/prompt").length, 1, "old prompt is never re-sent");
  assert.equal(context.testClients[1].state.phase, "ready");
});

// F. Ctrl+Enter
test("F Ctrl+Enter and Meta+Enter submit once; plain Enter does not", async () => {
  const press = async (init, expectedPosts) => {
    const {elements: e, calls} = await shell();
    e["daily-prompt"].value = "fixture prompt";
    let prevented = false;
    await e["daily-prompt"].handlers.keydown?.({key: "Enter", preventDefault() { prevented = true; }, ...init});
    await settle();
    assert.equal(posts(calls, "/prompt").length, expectedPosts, JSON.stringify(init));
    return prevented;
  };
  await press({ctrlKey: true}, 1);
  await press({metaKey: true}, 1);
  assert.equal(await press({}, 0), false, "plain Enter keeps its newline behaviour");
});

// G. Paperclip
test("G paperclip board states", async () => {
  const cases = [
    [undefined, /can’t verify/, "unconfirmed"],
    [{schema: "ghoti_paperclip_status/1", status: "RUNNING", pending_approvals: 2}, /running[\s\S]*2 approvals waiting|2 approvals waiting[\s\S]*running/i, "permission"],
    [{schema: "ghoti_paperclip_status/1", status: "RUNNING", pending_approvals: 0}, /running/i, "connected"],
    [{schema: "ghoti_paperclip_status/1", status: "STOPPED", pending_approvals: 0}, /stopped(?![\s\S]*waiting)/i, "attention"],
    [{schema: "ghoti_paperclip_status/1", status: "STOPPED", pending_approvals: 2}, /stopped[\s\S]*2 approvals waiting/i, "attention"],
    [{schema: "wrong/1", status: "RUNNING", pending_approvals: 1}, /can’t verify/, "unconfirmed"],
    [{schema: "ghoti_paperclip_status/1", status: "RUNNING", pending_approvals: 1.5}, /can’t verify/, "unconfirmed"],
    [{schema: "ghoti_paperclip_status/1", status: "RUNNING", pending_approvals: "2"}, /can’t verify/, "unconfirmed"],
  ];
  for (const [paperclip, pattern, state] of cases) {
    const {elements: e} = await shell({setup: d => { if (paperclip) d.integrations = {paperclip}; }});
    assert.match(e["daily-paperclip"].textContent, pattern, JSON.stringify(paperclip));
    assert.equal(e["daily-paperclip"].dataset.state, state, JSON.stringify(paperclip));
  }
});

test("G paperclip link href is never changed by JS", async () => {
  const {elements: e} = await shell({setup: d => { d.integrations = {paperclip: {schema: "ghoti_paperclip_status/1", status: "RUNNING", pending_approvals: 2}}; }});
  const link = e["daily-paperclip-link"];
  assert.ok(!link.attributeCalls.includes("href"));
  assert.equal(link.href, undefined);
  assert.equal(link.attributes.href, undefined);
});

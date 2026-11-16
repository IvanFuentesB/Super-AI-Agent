"use strict";
// State-honesty tests for the Computer and Paperclip views. Synthetic DOM/API only; never used by the served app.
// STATIC_ROOT may point at another static directory (used to run the same file against a baseline).
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = process.env.STATIC_ROOT || path.join(__dirname, "../dashboard_app/static");
const computerSource = path.join(root, "computer.js");
const {ComputerClient, statusTone, progressSteps, progressText, navState} = require(computerSource);
const STATES = ["created", "awaiting_permission", "running", "stopping", "stopped", "expired", "succeeded", "failed", "uncertain"];

// ---------------------------------------------------------------- client fixtures
const mkTask = (state, extra = {}) => ({schema: "ghoti_computer_task/1", task_id: "owned-task", generation: "owned-generation", state,
  scope: {operation: "create_note", filename: "owned-file", text: "fixture"},
  permission: state === "awaiting_permission" ? {request_id: "permission", expires_in_seconds: 60} : null,
  observation: {live: state === "running", image_version: 1}, result: {}, ...extra});
// `down` makes every request reject; otherwise queued replies are served in order (Error instances reject).
function clientFixture() {
  const calls = [], replies = [], f = {calls, replies, down: false};
  const local = {authenticated: true, reason: "fixture", request: async (url, options = {}) => {
    calls.push({url, ...options});
    if (f.down) throw new Error("fixture offline");
    const reply = replies.shift();
    if (reply instanceof Error) throw reply;
    assert.ok(reply, `unexpected fixture request ${url}`);
    return reply;
  }};
  let n = 0;
  f.client = new ComputerClient({local, makeId: () => `fixture-${++n}`, clock: () => 100});
  return f;
}
const accepted = (state, extra) => { const f = clientFixture(); f.client.accept(mkTask(state, extra)); return f; };

// ---------------------------------------------------------------- 1 unconfirmed Stop in navigation
test("1 a stopped task with unconfirmed cancellation shows Stop unconfirmed in navigation", () => {
  for (const extra of [{cancellation_confirmed: false}, {}, {cancellation_confirmed: undefined}]) {
    const {client} = accepted("stopped", extra);
    assert.deepEqual(navState(client), {text: "Stop unconfirmed", tone: "unconfirmed"}, JSON.stringify(extra));
    assert.equal(progressSteps(client)[2].state, "problem", `step 3 ${JSON.stringify(extra)}`);
  }
});
test("1 only a confirmed cancellation settles Running and clears the navigation badge", () => {
  const {client} = accepted("stopped", {cancellation_confirmed: true});
  assert.equal(progressSteps(client)[2].state, "done");
  assert.deepEqual(navState(client), {text: "", tone: ""});
});

// ---------------------------------------------------------------- 2 failed Stop request
function assertStopUnconfirmed(client, label) {
  assert.deepEqual(navState(client), {text: "Stop unconfirmed", tone: "unconfirmed"}, `${label} nav`);
  assert.match(progressText(client), /may still be acting/, `${label} progress`);
}
test("2 a failed Stop request gives the status line the unconfirmed tone, also while the connection stays down", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  assert.equal(statusTone(f.client), "unconfirmed", "after failed stop");
  await f.client.refresh();
  assert.equal(statusTone(f.client), "unconfirmed", "after a further failed refresh");
});
test("2 a failed Stop request reads as unconfirmed, not as a lost connection", async () => {
  const f = accepted("running");
  f.down = true;
  assert.equal(await f.client.stop(), false);
  assertStopUnconfirmed(f.client, "after failed stop");
  await f.client.refresh();
  assertStopUnconfirmed(f.client, "after a further failed refresh");
});
test("2 after a failed Stop, a poll still reporting running says Stop was not acknowledged, until Stop is confirmed", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  f.down = false;
  for (let i = 0; i < 2; i += 1) {
    f.replies.push(mkTask("running"));
    await f.client.refresh();
    assert.match(f.client.reason, /Stop was not acknowledged/, `poll ${i + 1}`);
    assert.match(f.client.reason, /still reported as running/, `poll ${i + 1}`);
    assert.equal(statusTone(f.client), "unconfirmed", `poll ${i + 1}`);
    assert.deepEqual(navState(f.client), {text: "Stop unconfirmed", tone: "unconfirmed"}, `poll ${i + 1}`);
  }
  f.replies.push(mkTask("stopped", {cancellation_confirmed: true}));
  assert.equal(await f.client.stop(), true);
  assert.match(f.client.reason, /Stopped/);
  assert.deepEqual(navState(f.client), {text: "", tone: ""});
  assert.doesNotMatch(f.client.reason, /not acknowledged/);
});
test("2 after a failed Stop, a poll reporting stopping or stopped is never 'not acknowledged'", async () => {
  for (const next of [mkTask("stopping"), mkTask("stopped", {cancellation_confirmed: true}), mkTask("stopped", {cancellation_confirmed: false})]) {
    const f = accepted("running");
    f.down = true;
    await f.client.stop();
    f.down = false;
    f.replies.push(next);
    await f.client.refresh();
    assert.doesNotMatch(f.client.reason, /not acknowledged/, `${next.state}/${next.cancellation_confirmed}`);
  }
});

// ---------------------------------------------------------------- 3 no "Task succeeded · waiting"
test("3 a verified success with no phase or reason reads as finished, not waiting", () => {
  const {client} = accepted("succeeded", {verification: "SUCCESS"});
  assert.doesNotMatch(client.reason, /waiting/);
  assert.equal(client.reason, "Finished and verified by readback.");
});
test("3 no state with no phase or reason ever says '· waiting'", () => {
  for (const state of STATES) {
    const {client} = accepted(state, {verification: state === "succeeded" ? "SUCCESS" : undefined});
    assert.ok(!client.reason.includes("· waiting"), `${state}: ${client.reason}`);
  }
});

// ---------------------------------------------------------------- 4 success without evidence is never verified
const unverifiedCases = [];
for (const verification of [undefined, "VERIFIED", "FAILED", null]) for (const result of [{}, {reason: "Readback matched"}]) unverifiedCases.push({verification, result});
test("guard 4 success without SUCCESS verification keeps attention tone and a problem final step", () => {
  for (const {verification, result} of unverifiedCases) {
    const {client} = accepted("succeeded", {verification, result});
    const label = JSON.stringify({verification, result});
    assert.equal(statusTone(client), "attention", label);
    assert.equal(progressSteps(client)[3].state, "problem", label);
  }
});
test("4 success without SUCCESS verification says not verified in reason, progress and navigation", () => {
  for (const {verification, result} of unverifiedCases) {
    const {client} = accepted("succeeded", {verification, result});
    const label = JSON.stringify({verification, result});
    assert.ok(client.reason.startsWith("Finished, but the result was not verified."), `${label}: ${client.reason}`);
    assert.match(progressText(client), /not verified/, label);
    assert.deepEqual(navState(client), {text: "Not verified", tone: "attention"}, label);
  }
});

// ---------------------------------------------------------------- 5 Paperclip under a failed runtime request
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
// options.stateFails is read on every request, so a test may flip it after load.
async function shell(options = {}) {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
  const data = {schema: "ghoti_deployed_runtime/1", deployment: {status: "NOT_INSTALLED"}, live_workers_running: 0,
    safe_operations: ["capability_lookup"], safe_workflows: [], jobs: [], memory: {obsidian_reference_count: 0, native_run_count: 0},
    learning: {status: "NOT_VERIFIED"}, computer_use: {status: "NOT_VERIFIED"}, observations: {
      scope: "Fixture observation window", verification_scope: "Transport is not task correctness", memory_status: "written", capabilities: [], receipts: []}};
  if (options.setup) options.setup(data);
  const ok = body => ({ok: true, json: async () => body});
  const context = {document: {getElementById: id => elements[id], createElement: tag => new Element(tag), querySelectorAll: () => [], addEventListener() {}, hidden: false},
    window: {addEventListener() {}}, navigator: {}, location: {hostname: "example.invalid"},
    fetch: async (url, init) => {
      if (url === "/api/runtime/state") { if (options.stateFails) throw new Error("fixture offline"); return ok(data); }
      const post = init?.method === "POST";
      if (url === "/api/runtime/chat" && !post) return ok({schema: "ghoti_chat_state/1", available: true, csrf_token: "fixture-csrf", reasoning_effort: "max", models: [{id: "openai-codex:gpt-6-astra"}], sessions: []});
      if (url.includes("/events")) return {ok: false, status: 500};
      return {ok: false, status: 403};
    },
    setTimeout() {}, clearTimeout() {}, AbortSignal, TextEncoder, Date, console,
    crypto: {randomUUID: (() => { let n = 0; return () => `fixture-id-${++n}`; })()}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(root, "chat.js"), "utf8"), context);
  vm.runInContext("globalThis.testClients=[]; const Base=GhotiChat.ChatClient; GhotiChat.ChatClient=class extends Base {constructor(o){super(o);testClients.push(this);}};", context);
  vm.runInContext(fs.readFileSync(path.join(root, "daily.js"), "utf8"), context);
  await settle();
  return {elements, context, data, options};
}
const refresh = async e => { await e["daily-refresh"].handlers.click(); await settle(); };
const board = (status, pending_approvals) => ({schema: "ghoti_paperclip_status/1", status, pending_approvals});

test("5a a failed runtime request from first load says the Paperclip status is unknown", async () => {
  const {elements: e} = await shell({stateFails: true});
  const text = e["daily-paperclip"].textContent;
  assert.match(text, /Couldn’t reach the runtime/);
  assert.match(text, /unknown/);
  assert.doesNotMatch(text, /doesn’t report its status/);
  assert.doesNotMatch(text, /\d+ approvals? waiting/);
  assert.equal(e["daily-paperclip"].dataset.state, "unavailable");
});
test("5b a later failed request shows the last report only as dated, possibly stale history", async () => {
  const s = await shell({setup: d => { d.integrations = {paperclip: board("STOPPED", 2)}; }});
  const e = s.elements;
  assert.match(e["daily-paperclip"].textContent, /^The Paperclip board is stopped/, "precondition: first load is reported");
  s.options.stateFails = true;
  await refresh(e);
  const text = e["daily-paperclip"].textContent;
  assert.match(text, /unknown/);
  assert.match(text, /Last reported at/);
  assert.match(text, /stopped · 2 approvals waiting/);
  assert.match(text, /may be out of date/);
  assert.doesNotMatch(text, /^The Paperclip board is stopped/);
  assert.equal(e["daily-paperclip"].dataset.state, "unavailable");
  await refresh(e);
  assert.equal(e["daily-paperclip"].textContent, text, "a second identical failure changes nothing");
});
test("guard 5c a reachable runtime without a Paperclip report stays unverified, and a later failure shows no 'Last reported'", async () => {
  const s = await shell();
  const e = s.elements;
  assert.match(e["daily-paperclip"].textContent, /can’t verify/);
  assert.match(e["daily-paperclip"].textContent, /doesn’t report its status yet/);
  assert.equal(e["daily-paperclip"].dataset.state, "unconfirmed");
  s.options.stateFails = true;
  await refresh(e);
  assert.doesNotMatch(e["daily-paperclip"].textContent, /Last reported/);
});

// ---------------------------------------------------------------- 6 menu attention
test("6 an unconfirmed Computer badge raises the menu to attention; permission still wins", async () => {
  const {elements: e, context} = await shell();
  const kick = () => { const client = context.testClients.at(-1); client.changed(); };
  assert.equal(e["daily-menu"].dataset.state, "", "precondition: calm menu");
  e["daily-nav-computer-state"].dataset.state = "unconfirmed";
  kick();
  assert.equal(e["daily-menu"].dataset.state, "attention");
  e["daily-nav-memory-state"].dataset.state = "permission";
  kick();
  assert.equal(e["daily-menu"].dataset.state, "permission");
});

// ---------------------------------------------------------------- 7 render level
function load() {
  const writes = [], elements = {}, document = {activeElement: null};
  const make = id => {
    const store = {id, tagName: "div", children: [], attrs: {}, focusCalls: 0, scrollCalls: 0, inner: [], handlers: {}};
    store.dataset = new Proxy({}, {set(t, k, v) { writes.push(`${id}.dataset.${String(k)}`); t[k] = v; return true; }});
    const el = new Proxy(store, {set(t, k, v) { if (typeof k === "string") writes.push(`${id}.${k}`); t[k] = v; return true; }});
    Object.assign(store, {
      setAttribute(k, v) { writes.push(`${id}.setAttribute(${k})`); store.attrs[k] = String(v); },
      getAttribute(k) { return Object.hasOwn(store.attrs, k) ? store.attrs[k] : null; },
      removeAttribute(k) { writes.push(`${id}.removeAttribute(${k})`); delete store.attrs[k]; },
      replaceChildren(...nodes) { writes.push(`${id}.replaceChildren`); store.children = nodes; },
      append(...nodes) { writes.push(`${id}.append`); store.children.push(...nodes); },
      addEventListener(k, f) { store.handlers[k] = f; },
      focus() { store.focusCalls += 1; document.activeElement = el; },
      scrollIntoView() { store.scrollCalls += 1; },
      contains(node) { return node === el || store.inner.includes(node); },
    });
    return el;
  };
  const el = id => elements[id] ||= make(id);
  document.getElementById = el;
  document.createElement = tag => { const e = make(`<${tag}>`); e.tagName = tag; return e; };
  el("computer-approval").inner.push(el("computer-approve"), el("computer-deny"));
  el("computer-input-mode").value = "text"; el("computer-text").value = ""; el("computer-wait").value = "0";
  const context = {document, window: {addEventListener() {}}, setInterval() {}, setTimeout() {}, console,
    performance: {now: () => 1000}, crypto: {randomUUID: () => "fixture-id"},
    GhotiLocal: {authenticated: true, reason: "", ready: new Promise(() => {}), request: async () => { throw new Error("unexpected request"); }}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(computerSource, "utf8"), context);
  const ctrl = context.GhotiComputer;
  assert.ok(ctrl, "GhotiComputer controller is exposed");
  ctrl.health = {schema: "ghoti_computer/1", can_start: true}; ctrl.connected = true; ctrl.reason = "Ready.";
  const count = prefixes => writes.filter(w => prefixes.some(p => w.startsWith(p))).length;
  return {ctrl, el, writes, count, mark: () => { writes.length = 0; }};
}
test("7 approval focus is taken once; returning to the panel scrolls once and never steals focus", () => {
  const h = load();
  const approval = h.el("computer-approval");
  h.ctrl.accept(mkTask("awaiting_permission"), {replace: true});
  assert.equal(approval.focusCalls, 1, "first render focuses the approval card");
  for (let i = 0; i < 10; i += 1) h.ctrl.changed();
  assert.equal(approval.focusCalls, 1);
  assert.equal(approval.scrollCalls, 0, "no scroll while the panel stays open");
  h.el("daily-panel-computer").hidden = true;
  h.ctrl.changed();
  h.el("daily-panel-computer").hidden = false;
  for (let i = 0; i < 5; i += 1) h.ctrl.changed();
  assert.equal(approval.focusCalls, 1, "no focus stealing on return");
  assert.equal(approval.scrollCalls, 1, "scrolled into view exactly once for the return");
});
test("7 unchanged repeated renders write nothing to the live regions or the navigation badge", () => {
  const h = load();
  h.ctrl.accept(mkTask("awaiting_permission"), {replace: true});
  h.ctrl.changed();
  h.mark();
  for (let i = 0; i < 10; i += 1) h.ctrl.changed();
  assert.equal(h.count(["computer-status", "computer-progress", "daily-nav-computer-state"]), 0, JSON.stringify(h.writes));
});

// ---------------------------------------------------------------- 8 markup
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const css = fs.readFileSync(path.join(root, "daily.css"), "utf8");
const tagOf = id => {
  const m = new RegExp(`<[a-zA-Z][^>]*\\bid="${id}"[^>]*>`).exec(html);
  assert.ok(m, `#${id} exists`);
  return m[0];
};
const attrOf = (tag, name) => { const m = new RegExp(`\\s${name}="([^"]*)"`).exec(tag); return m ? m[1].replaceAll("&quot;", '"').replaceAll("&amp;", "&") : null; };
test("8 scrollable output boxes are focusable, have a role and a non-empty accessible name", () => {
  for (const id of ["daily-chat-timings", "computer-scope", "computer-accessibility", "computer-result", "daily-computer-evidence", "daily-deployment", "daily-memory-evidence"]) {
    const tag = tagOf(id);
    assert.equal(attrOf(tag, "tabindex"), "0", `#${id} tabindex`);
    assert.ok(attrOf(tag, "role"), `#${id} role`);
    assert.ok((attrOf(tag, "aria-label") || "").trim(), `#${id} aria-label`);
  }
});
test("8 the wait select has short option labels and a real description; the placeholder is short", () => {
  const select = new RegExp(`<select[^>]*\\bid="computer-wait"[^>]*>([\\s\\S]*?)</select>`).exec(html);
  assert.ok(select, "#computer-wait exists");
  const labels = [...select[1].matchAll(/<option[^>]*>([^<]*)<\/option>/g)].map(m => m[1]);
  assert.ok(labels.length >= 2, "has options");
  for (const label of labels) assert.ok(label.length <= 28, `"${label}" is ${label.length} characters`);
  const described = attrOf(tagOf("computer-wait"), "aria-describedby");
  assert.ok(described, "aria-describedby present");
  for (const id of described.split(/\s+/)) assert.ok(new RegExp(`\\bid="${id}"`).test(html), `describedby target #${id} exists`);
  const placeholder = attrOf(tagOf("computer-text"), "placeholder");
  assert.ok(placeholder, "placeholder present");
  assert.ok(placeholder.length <= 32, `placeholder is ${placeholder.length} characters`);
});
test("8 forced-colors mode draws a real outline when the composer textarea has keyboard focus", () => {
  const start = css.indexOf("@media (forced-colors: active)");
  assert.ok(start >= 0, "forced-colors block exists");
  let depth = 0, end = -1;
  for (let i = css.indexOf("{", start); i < css.length; i += 1) {
    if (css[i] === "{") depth += 1;
    if (css[i] === "}" && --depth === 0) { end = i; break; }
  }
  assert.ok(end > start, "block is closed");
  const block = css.slice(start, end);
  const rule = /\.daily-composer:has\(textarea:focus-visible\)\s*\{([^}]*)\}/.exec(block);
  assert.ok(rule, "composer focus rule inside the forced-colors block");
  assert.match(rule[1], /\boutline\s*:/);
});

// ---------------------------------------------------------------- R1/R2 repair: Stop intent bound to its task, structured verification only
const unresolvedNav = {text: "Stop unconfirmed", tone: "unconfirmed"};
function assertUnresolved(client, label) {
  assert.deepEqual(navState(client), unresolvedNav, `${label} nav`);
  assert.equal(statusTone(client), "unconfirmed", `${label} tone`);
  assert.match(progressText(client), /not confirmed/, `${label} progress`);
}
test("R1 a pending Stop is unresolved in every view before the transport resolves", async () => {
  const f = accepted("running");
  let answer;
  f.client.local.request = () => new Promise(resolve => { answer = resolve; });
  const stopping = f.client.stop();
  assertUnresolved(f.client, "pending");
  assert.match(f.client.reason, /not yet acknowledged/);
  // A running poll arriving while Stop is still in flight does not settle it, nor claim it was missed.
  f.client.accept(mkTask("running"));
  assertUnresolved(f.client, "poll while pending");
  assert.match(f.client.reason, /not yet acknowledged/);
  answer(mkTask("stopping"));
  await stopping;
  assertUnresolved(f.client, "stopping reply");
  assert.match(f.client.reason, /Stop requested/);
  f.client.accept(mkTask("stopped", {cancellation_confirmed: true}));
  assert.deepEqual(navState(f.client), {text: "", tone: ""});
});
test("R1 a failed Stop followed by running and stopping polls stays unresolved in every view", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  f.down = false;
  for (const next of [mkTask("running"), mkTask("stopping"), mkTask("running")]) {
    f.replies.push(next);
    await f.client.refresh();
    assertUnresolved(f.client, next.state);
  }
});
test("R1 a snapshot that omits or falsifies cancellation_confirmed never clears Stop", async () => {
  for (const extra of [{}, {cancellation_confirmed: undefined}, {cancellation_confirmed: null}, {cancellation_confirmed: false}, {cancellation_confirmed: "true"}]) {
    const f = accepted("running");
    f.down = true;
    await f.client.stop();
    f.client.accept(mkTask("stopped", extra));
    assertUnresolved(f.client, JSON.stringify(extra));
    f.client.accept(mkTask("running", extra));
    assertUnresolved(f.client, `running ${JSON.stringify(extra)}`);
  }
});
test("R1 only stopped with cancellation_confirmed true clears the Stop warning", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  f.client.accept(mkTask("stopped", {cancellation_confirmed: true}));
  assert.deepEqual(navState(f.client), {text: "", tone: ""});
  assert.equal(statusTone(f.client), "");
  assert.match(f.client.reason, /^Stopped/);
  // A later unrelated snapshot of the same task is not resurrected into a warning.
  f.client.accept(mkTask("running"));
  assert.deepEqual(navState(f.client), {text: "Running", tone: "running"});
});
test("R1 navigation and rendering cannot clear Stop; a different task does not inherit it", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  f.client.onChange(f.client);
  assertUnresolved(f.client, "after change notification");
  // An unrelated new task is accepted deliberately (start path): it must read as an ordinary running task.
  const other = mkTask("running", {task_id: "other-task", generation: "other-generation"});
  f.client.accept(other, {replace: true});
  assert.deepEqual(navState(f.client), {text: "Running", tone: "running"});
  assert.equal(statusTone(f.client), "running");
  assert.doesNotMatch(f.client.reason, /Stop/);
  assert.doesNotMatch(progressText(f.client), /Stop/);
  // A stale, out-of-order snapshot of the old task is rejected, so it neither resurrects nor clears anything on the new task.
  assert.throws(() => f.client.accept(mkTask("stopped", {cancellation_confirmed: true})), /identity/);
  assert.deepEqual(navState(f.client), {text: "Running", tone: "running"});
  // The warning stays bound to the old task: it is still unresolved if that task is shown again unconfirmed.
  f.client.accept(mkTask("running"), {replace: true});
  assertUnresolved(f.client, "old task shown again");
});
test("R1 a snapshot for another task cannot clear the Stop warning of the current task", async () => {
  const f = accepted("running");
  f.down = true;
  await f.client.stop();
  const other = mkTask("stopped", {task_id: "other-task", generation: "other-generation", cancellation_confirmed: true});
  f.client.accept(other, {replace: true});
  f.client.accept(mkTask("running"), {replace: true});
  assertUnresolved(f.client, "after other-task confirmation");
});
test("R2 free-text reasons never produce verified wording without SUCCESS verification", () => {
  for (const verification of [undefined, null, "UNVERIFIED", "VERIFIED", "FAILED"]) {
    for (const extra of [{reason: "Finished and verified by readback."}, {result: {reason: "Finished and verified by readback."}},
      {reason: "Verified.", result: {reason: "verified by readback"}}]) {
      const {client} = accepted("succeeded", {verification, ...extra});
      const label = JSON.stringify({verification, ...extra});
      assert.ok(client.reason.startsWith("Finished, but the result was not verified."), `${label}: ${client.reason}`);
      assert.match(client.reason, /Reported: /, label);
      assert.doesNotMatch(client.reason.split(" Reported: ")[0], /verified by readback/, label);
      assert.equal(statusTone(client), "attention", label);
      assert.match(progressText(client), /not verified/, label);
      assert.deepEqual(navState(client), {text: "Not verified", tone: "attention"}, label);
    }
  }
});
test("R2 verified wording comes only from verification SUCCESS", () => {
  const {client} = accepted("succeeded", {verification: "SUCCESS", reason: "anything"});
  assert.equal(client.reason, "Finished and verified by readback.");
  assert.equal(statusTone(client), "success");
  assert.deepEqual(navState(client), {text: "", tone: ""});
});

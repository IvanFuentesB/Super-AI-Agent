"use strict";
// Synthetic DOM/API responses exercise the real renderer; never used by the served app.
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.join(__dirname, "../dashboard_app/static");
class Element {
  constructor(tag = "div") { this.tagName = tag; this.children = []; this.handlers = {}; this.dataset = {}; this.value = ""; this.hidden = false; this.disabled = false; this._text = ""; this.attributes = {}; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(" "); }
  set innerHTML(_) { throw new Error("Unsafe DOM sink"); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute(k, v) { this.attributes[k] = v; }
  addEventListener(k, f) { this.handlers[k] = f; }
  focus() {}
}
async function shell() {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  assert.match(html, /id="daily-shell"/, "Daily shell is the default surface");
  assert.doesNotMatch(html, /src="\/static\/(?:app|runtime)\.js/, "Legacy actions must not boot in the daily shell");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
  const calls = [];
  const data = {schema: "ghoti_deployed_runtime/1", deployment: {status: "NOT_INSTALLED"}, live_workers_running: 0,
    safe_operations: ["capability_lookup"], safe_workflows: [], jobs: [], memory: {obsidian_reference_count: 0, native_run_count: 0},
    learning: {status: "NOT_VERIFIED"}, computer_use: {status: "NOT_VERIFIED"}, observations: {
      scope: "Fixture observation window", verification_scope: "Transport is not task correctness", memory_status: "MEMORY_STALE",
      capabilities: [{capability_id: "<img src=x onerror=evil()>", status: "UNUSED", usage_count: 0, attempt_count: 0}], receipts: []}};
  const timers = [];
  const registrations = [];
  const context = {document: {getElementById: id => elements[id], createElement: tag => new Element(tag),
      querySelectorAll: () => [], addEventListener: () => {}, hidden: false},
    window: {addEventListener: () => {}}, navigator: {serviceWorker: {register: async url => {registrations.push(url);}}}, location: {hostname: "127.0.0.1"},
    fetch: async (url, options) => { calls.push({url, options}); return url === "/api/runtime/state" ?
      {ok: true, json: async () => data} : {ok: false, status: 403}; },
    setTimeout: f => {timers.push(f);}, clearTimeout: () => {}, AbortSignal, TextEncoder, Date, console,
    crypto: {randomUUID: () => "fixture-id"}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(root, "chat.js"), "utf8"), context);
  vm.runInContext("globalThis.testClients=[]; const Base=GhotiChat.ChatClient; GhotiChat.ChatClient=class extends Base {constructor(options){super(options);testClients.push(this);}};", context);
  vm.runInContext(fs.readFileSync(path.join(root, "daily.js"), "utf8"), context);
  await new Promise(resolve => setImmediate(resolve));
  return {elements, context, calls, timers, registrations, data};
}

test("reasoning preference is wired idle-only and effective effort is truthful", async () => {
  const {elements:e,context,calls}=await shell();
  const client=context.testClients[0];
  Object.assign(client.state,{phase:"ready",available:true,modelId:"openai-codex:gpt-6-astra",effort:null});
  client.changed();
  e["daily-chat-mode"].value="fast";
  e["daily-chat-mode"].handlers.change();
  assert.equal(client.state.mode,"fast");
  assert.match(e["daily-model"].textContent,/unverified/i);
  client.state.effort="low";client.state.phase="running";client.changed();
  assert.match(e["daily-model"].textContent,/low/);
  assert.equal(e["daily-chat-mode"].disabled,true);
  assert.ok(calls.every(c=>!c.options?.method||c.options.method==="GET"));
});

test("daily shell shows real empty runtime state and unavailable chat, with no fake activity", async () => {
  const {elements: e, calls} = await shell();
  assert.match(e["daily-chat-state"].textContent, /unavailable/i);
  assert.equal(e["daily-send"].disabled, true);
  assert.match(e["daily-jobs"].textContent, /No recorded/);
  assert.match(e["daily-workers"].textContent, /No local workers running/);
  assert.match(e["daily-capabilities"].textContent, /<img src=x/);
  assert.equal(e["daily-run"].disabled, false);
  assert.ok(calls.every(c => !c.options?.method || c.options.method === "GET"));
});

test("failed refresh clears worker, memory, computer and job claims", async () => {
  const {elements: e, context} = await shell();
  context.fetch = async () => {throw new Error("fixture offline");};
  await e["daily-refresh"].handlers.click();
  for (const id of ["daily-workers", "daily-memory", "daily-computer", "daily-jobs", "daily-capabilities"]) {
    assert.match(e[id].textContent, /unavailable|stale/i, id);
  }
  assert.equal(e["daily-run"].disabled, true);
});

test("verified deployed runtime retires the root offline shell, not a different scope", async () => {
  const {registrations} = await shell();
  assert.equal(registrations.length, 1);
  assert.equal(registrations[0].split("?")[0], "/service-worker.js");
});

test("retired chat callbacks cannot change current controls or abandon an active client", async () => {
  const {elements: e, context} = await shell();
  const old = context.testClients[0];
  old.state.phase = "complete";
  old.changed();
  await e["daily-new"].handlers.click();
  assert.equal(context.testClients.length, 2);
  const current = context.testClients[1];
  current.state.phase = "running";
  current.state.sessionId = "fixture-current-session";
  current.changed();
  old.changed();
  assert.equal(e["daily-new"].disabled, true);
  assert.equal(e["daily-cancel"].disabled, false);
  e["daily-new"].disabled = false; // A stale DOM alone must not authorize replacement.
  await e["daily-new"].handlers.click();
  assert.equal(context.testClients.length, 2);
});

test("bounded local tasks keep exact operations, one submission and saved results", async () => {
  const {elements: e, context, data} = await shell();
  const writes = [];
  let resolveRun;
  context.fetch = async (url, options) => {
    if (url === "/api/runtime/state") return {ok: true, json: async () => data};
    writes.push({url, options});
    if (url === "/api/runtime/run") return new Promise(resolve => {resolveRun = resolve;});
    if (url === "/api/runtime/result/fixture-task") return {ok: true, json: async () => ({task_id: "fixture-task", text: "<script>fixture saved text only</script>"})};
    throw new Error("Unexpected fixture request");
  };
  const submit = () => e["daily-task-form"].handlers.submit({preventDefault() {}});
  e["daily-operation"].value = "not-offered";
  await submit();
  assert.equal(writes.length, 0);
  e["daily-operation"].value = "capability_lookup";
  e["daily-task-text"].value = "fixture task text";
  const running = submit();
  await submit();
  assert.equal(writes.length, 1);
  assert.deepEqual(JSON.parse(writes[0].options.body), {operation: "capability_lookup", text: "fixture task text"});
  resolveRun({ok: true, json: async () => ({state: "succeeded", task_id: "fixture-task"})});
  await running;
  assert.match(e["daily-task-result"].textContent, /fixture-task/);
  data.jobs = [{task_id: "fixture-task", title: "Fixture record", state: "succeeded"}];
  await e["daily-refresh"].handlers.click();
  const row = e["daily-jobs"].children[0];
  await row.children.find(child => child.tagName === "button").handlers.click();
  assert.equal(row.children.at(-1).children[0].textContent, "<script>fixture saved text only</script>");
  assert.equal(row.children.at(-1).children[0].tagName, "p");
});

test("human outcomes separate failure, local checks and provider eligibility", async () => {
  const {elements: e, data} = await shell();
  const cases = [
    [{state: "failed", verification_scope: "exact registry result comparison"}, "Couldn’t finish"],
    [{state: "blocked", verification: "SUCCESS"}, "Blocked"],
    [{state: "interrupted"}, "Interrupted"],
    [{state: "succeeded", verification_scope: "not verified", route: {selected: {verified: true}}}, "Finished · review needed"],
    [{state: "succeeded", verification_scope: "exact registry result comparison"}, "Completed · local checks passed"],
    [{state: "succeeded", verification_scope: "bounded nonempty safe text; factual accuracy requires human review"}, "Draft ready · review needed"],
    [{state: "succeeded", result: {checked: false, check_notes: ["exact registry result comparison"]}}, "Finished · review needed"],
    [{state: "executing", running: false}, "Outcome not confirmed"],
    [{state: "executing", running: true}, "Working"],
  ];
  for (const [job, expected] of cases) {
    data.jobs = [{title: "Fixture", ...job}];
    await e["daily-refresh"].handlers.click();
    const row = e["daily-jobs"].children[0];
    assert.ok(row.children[1].textContent.startsWith(expected), JSON.stringify(job));
    assert.equal(row.children[2].tagName, "details", "Raw evidence is disclosed explicitly");
  }
});

test("malformed input never creates work and saved result identity must match", async () => {
  const {elements: e, context, calls, data} = await shell();
  const before = calls.length;
  e["daily-operation"].value = "capability_lookup";
  for (const text of [" ", "a".repeat(4001), "界".repeat(3000)]) {
    e["daily-task-text"].value = text;
    await e["daily-task-form"].handlers.submit({preventDefault() {}});
    assert.equal(calls.length, before);
  }
  e["daily-prompt"].value = "/unsafe-command";
  await e["daily-chat-form"].handlers.submit({preventDefault() {}});
  assert.equal(e["daily-input-error"].hidden, false);
  assert.equal(e["daily-prompt"].attributes["aria-invalid"], "true");
  assert.equal(calls.length, before);
  data.jobs = [{task_id: "fixture-task", state: "succeeded", title: "Lookup"}];
  await e["daily-refresh"].handlers.click();
  context.fetch = async () => ({ok: true, json: async () => ({task_id: "wrong-task", text: "Do not display"})});
  const row = e["daily-jobs"].children[0];
  await row.children.find(child => child.tagName === "button").handlers.click();
  assert.match(row.children.at(-1).textContent, /unavailable/);
  assert.doesNotMatch(row.children.at(-1).textContent, /Do not display/);
});

test("loaded memory filter and recent work disclosure are bounded and read only", async () => {
  const {elements: e, data, calls} = await shell();
  data.memory.startup_references = [{system: "obsidian", reason: "Project brief"}, {system: "brain", reason: "Reading notes"}];
  data.jobs = Array.from({length: 8}, (_, i) => ({title: `Fixture ${i}`, state: "succeeded"}));
  await e["daily-refresh"].handlers.click();
  assert.equal(e["daily-jobs"].children.length, 5);
  assert.equal(e["daily-more-jobs"].hidden, false);
  e["daily-more-jobs"].handlers.click();
  assert.equal(e["daily-jobs"].children.length, 8);
  e["daily-memory-search"].value = "brief";
  e["daily-memory-search"].handlers.input();
  assert.equal(e["daily-memory-list"].children.length, 1);
  assert.match(e["daily-memory-list"].textContent, /Project brief/);
  assert.ok(calls.every(c => !c.options?.method));
});

test("hostile reply and permission strings remain text; permission node is stable until cleared", async () => {
  const {elements: e, context} = await shell();
  const client = context.testClients[0];
  const hostile = '<img src=x onerror="evil()"><script>evil()</script>';
  Object.assign(client.state, {phase: "permission", available: true, sessionId: "fixture-session",
    messages: [{role: "assistant", text: hostile}], permissions: [{request_id: "fixture-request", title: hostile,
      description: hostile, options: [{id: "deny"}, {id: "allow_once"}]}]});
  client.changed();
  const permission = e["daily-permissions"].children[0];
  assert.equal(e["daily-conversation"].children[0].children[1].textContent, hostile);
  assert.equal(permission.children[1].textContent, hostile);
  client.changed();
  assert.equal(e["daily-permissions"].children[0], permission);
  client.state.phase = "disconnected";
  client.changed();
  assert.equal(e["daily-permissions"].hidden, true);
  assert.equal(e["daily-permissions"].children.length, 0);
  assert.equal(e["daily-send"].disabled, true);
});

test("current conversation is live while other session rows are explicitly snapshots", async () => {
  const {elements: e, context} = await shell();
  const client = context.testClients[0];
  Object.assign(client.state, {phase: "running", sessionId: "fixture-current",
    sessions: [{session_id: "fixture-old", state: "idle", model_id: "fixture-model"}], sessionsStatus: "ready"});
  client.changed();
  assert.match(e["daily-sessions"].textContent, /Last reported: At rest/);
  assert.match(e["daily-sessions"].textContent, /Current conversation Ghoti is working/);
  const current = e["daily-history-list"].children.at(-1);
  assert.equal(current.children.find(child => child.tagName === "button").disabled, true);
  client.state.phase = "disconnected";
  client.changed();
  assert.match(e["daily-chat-state"].textContent, /Stop is not confirmed/);
  Object.assign(client.state, {phase: "failed", reason: "tool_cancellation_uncertain: technical details"});
  client.changed();
  assert.match(e["daily-chat-state"].textContent, /Stop could not be confirmed/);
  assert.doesNotMatch(e["daily-chat-state"].textContent, /technical details/);
});

test("retired history refresh rejection cannot overwrite a new client snapshot", async () => {
  const {elements: e, context, data} = await shell();
  const old = context.testClients[0];
  old.state.phase = "complete";
  let rejectOld;
  context.fetch = () => new Promise((_, reject) => {rejectOld = reject;});
  const refreshing = e["daily-history-refresh"].handlers.click();
  context.fetch = async url => ({ok: true, json: async () => url === "/api/runtime/state" ? data : ({
    schema: "ghoti_chat_state/1", available: true, csrf_token: "fixture", reasoning_effort: "max",
    models: [{id: "openai-codex:gpt-6-astra"}], sessions: [{session_id: "new-saved", state: "idle", model_id: "openai-codex:gpt-6-astra"}]
  })});
  await e["daily-new"].handlers.click();
  const valid = e["daily-history-list"].textContent;
  assert.match(valid, /Read saved replies/);
  rejectOld(new Error("old request failed"));
  await refreshing;
  assert.equal(e["daily-history-list"].textContent, valid);
});

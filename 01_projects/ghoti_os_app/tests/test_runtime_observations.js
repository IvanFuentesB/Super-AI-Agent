"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const staticRoot = path.join(__dirname, "../dashboard_app/static");

class Element {
  constructor(tag = "div") { this.tagName = tag; this.children = []; this.value = ""; this.handlers = {}; this._text = ""; }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join("\n"); }
  set innerHTML(value) { throw new Error("Untrusted observations must not use innerHTML"); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this._text = ""; this.children = children; }
  addEventListener(name, callback) { this.handlers[name] = callback; }
}

async function render(data) {
  const html = fs.readFileSync(path.join(staticRoot, "index.html"), "utf8");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  for (const id of ["runtime-observations", "runtime-capabilities", "runtime-receipts"]) {
    assert.ok(elements[id], `Missing native-observation panel element: ${id}`);
  }
  let refresh;
  const listeners = {};
  const context = { document: {
    getElementById: id => elements[id], createElement: tag => new Element(tag),
    addEventListener: (name, callback) => { listeners[name] = callback; },
  }, fetch: async url => {
    assert.equal(url, "/api/runtime/state");
    return { ok: true, json: async () => data };
  }, setInterval: callback => { refresh = callback; }, Date };
  vm.runInNewContext(fs.readFileSync(path.join(staticRoot, "runtime.js"), "utf8"), context);
  listeners["ghoti-runtime-ready"]();
  await new Promise(resolve => setImmediate(resolve));
  return { elements, context, refresh };
}

function state() {
  return { deployment: { status: "RUNNING", release_commit: "fixture-release" },
    live_workers_running: 0, memory: { obsidian_reference_count: 3, native_run_count: 1 },
    learning: { status: "CANDIDATE_ONLY" }, jobs: [], observations: {
      scope: "Latest up to 20 finalized turn records; counts cover this window only",
      verification_scope: "Hermes turn observed; task correctness not established",
      memory_status: "written", record_count: 1, invalid_records: 0, active_count: 1,
      pending_completion: false, capabilities_truncated: false,
      capabilities: [{ capability_id: "tool/read_file", status: "ACTIVE", usage_count: 2, attempt_count: 2,
        last_used: "2026-01-01T00:00:00+00:00", last_task: "task-fixture", model: "fixture-model", harness: "hermes",
        impact: "Framework reported ok; task correctness not established <img src=x onerror=throw>" }],
      receipts: [{ task_id: "task-fixture", task: "Observed fixture", state: "completed", model: "fixture-model",
        harness: "hermes", cost: "unknown", memory_status: "written", source: "ghoti_hermes_turns/task-fixture.json",
        usage_counted: ["tool/read_file"], selected_not_invoked: ["tool/terminal"] }],
    } };
}

test("a failed refresh removes stale capability claims and marks memory unverified", async () => {
  const { elements, context, refresh } = await render(state());
  context.fetch = async () => { throw new Error("Runtime state unavailable"); };
  await refresh();
  assert.match(elements["runtime-observations"].textContent, /MEMORY_STALE/);
  assert.equal(elements["runtime-capabilities"].children.length, 0);
  assert.equal(elements["runtime-receipts"].children.length, 0);
  assert.doesNotMatch(elements["runtime-capabilities"].textContent, /ACTIVE/);
});

test("existing panel renders recorded usage and memory without inventing live workers", async () => {
  const { elements } = await render(state());
  assert.equal(elements["global-agent-state"].textContent, "IDLE");
  assert.match(elements["runtime-observations"].textContent, /written/);
  assert.match(elements["runtime-observations"].textContent, /this window only/);
  assert.match(elements["runtime-observations"].textContent, /task correctness not established/);
  const usage = elements["runtime-capabilities"].textContent;
  for (const fragment of ["tool/read_file", "ACTIVE", "2 successful", "2 attempted", "task-fixture", "fixture-model", "hermes", "2026-01-01", "<img src=x"]) {
    assert.ok(usage.includes(fragment), `Missing usage field: ${fragment}`);
  }
  const receipts = elements["runtime-receipts"].textContent;
  for (const fragment of ["task-fixture", "written", "tool/terminal", "ghoti_hermes_turns/task-fixture.json", "unknown"]) {
    assert.ok(receipts.includes(fragment), `Missing receipt field: ${fragment}`);
  }
  assert.equal(elements["runtime-capabilities"].children[0].tagName, "article");
});

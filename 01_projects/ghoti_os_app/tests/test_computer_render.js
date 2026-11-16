"use strict";
// Render-level tests for the Computer view. Synthetic DOM only; never used by the served app.
// COMPUTER_JS may point at another copy of computer.js (used to check a baseline).
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const source = process.env.COMPUTER_JS || path.join(__dirname, "../dashboard_app/static/computer.js");

// Every property set, attribute change and child replacement is logged, even when the value is unchanged.
function load() {
  const writes = [];
  const elements = {};
  const document = {activeElement: null};
  const make = id => {
    const store = {id, tagName: "div", children: [], attrs: {}, focusCalls: 0, inner: [], handlers: {}};
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
      contains(node) { return node === el || store.inner.includes(node); },
    });
    return el;
  };
  const el = id => elements[id] ||= make(id);
  document.getElementById = el;
  document.createElement = tag => { const e = make(`<${tag}>`); e.tagName = tag; return e; };
  const approval = el("computer-approval");
  approval.inner.push(el("computer-approve"), el("computer-deny"));
  el("computer-input-mode").value = "text";
  el("computer-text").value = "";
  el("computer-wait").value = "0";
  const context = {document, window: {addEventListener() {}}, setInterval() {}, setTimeout() {}, console,
    performance: {now: () => 1000}, crypto: {randomUUID: () => "fixture-id"},
    GhotiLocal: {authenticated: true, reason: "", ready: new Promise(() => {}), request: async () => { throw new Error("unexpected request"); }}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(source, "utf8"), context);
  const ctrl = context.GhotiComputer;
  assert.ok(ctrl, "GhotiComputer controller is exposed");
  const task = (state, extra = {}) => ({schema: "ghoti_computer_task/1", task_id: "owned-task", generation: "owned-generation", state,
    scope: {operation: "create_note", filename: "owned-file"}, observation: {live: state === "running", image_version: 1},
    permission: state === "awaiting_permission" ? {request_id: "p1", expires_in_seconds: 60} : null,
    cancellation_confirmed: state === "stopped", result: {}, ...extra});
  const ready = () => { ctrl.health = {schema: "ghoti_computer/1", can_start: true}; ctrl.connected = true; ctrl.reason = "Ready."; };
  const count = prefix => writes.filter(w => w.startsWith(prefix)).length;
  return {ctrl, el, writes, document, task, ready, count, context, mark: () => { writes.length = 0; }};
}
const states = {
  idle: t => null,
  awaiting_permission: t => t("awaiting_permission"),
  running: t => t("running", {phase: "typing"}),
  succeeded: t => t("succeeded", {verification: "SUCCESS", result: {verified: true}}),
};

for (const [name, make] of Object.entries(states)) {
  test(`1 stable DOM: a second identical render writes nothing (${name})`, () => {
    const h = load();
    h.ready();
    const task = make(h.task);
    if (task) h.ctrl.accept(task, {replace: true}); else h.ctrl.changed();
    h.ctrl.changed();
    h.mark();
    h.ctrl.changed();
    assert.deepEqual(h.writes, []);
  });
}

test("1 a real transition writes the new status and progress text exactly once", () => {
  const h = load();
  h.ready();
  h.ctrl.accept(h.task("running", {phase: "typing"}), {replace: true});
  h.ctrl.changed();
  h.mark();
  h.ctrl.accept(h.task("succeeded", {verification: "SUCCESS"}), {replace: true});
  h.ctrl.changed();
  h.ctrl.changed();
  assert.equal(h.count("computer-status.textContent"), 1);
  assert.equal(h.count("computer-progress.textContent"), 1);
  assert.match(h.el("computer-progress").textContent, /Finished and verified/);
});

test("2 approval focus happens once per request, even if the user moved focus", () => {
  const h = load();
  h.ready();
  const approval = h.el("computer-approval");
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  assert.equal(approval.focusCalls, 1);
  const elsewhere = h.el("computer-text");
  h.document.activeElement = elsewhere;
  h.ctrl.changed();
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 1);
  assert.equal(h.document.activeElement, elsewhere, "focus is not stolen back");
  h.ctrl.accept(h.task("awaiting_permission", {permission: {request_id: "p2", expires_in_seconds: 60}}), {replace: true});
  assert.equal(approval.focusCalls, 2, "a new request focuses once again");
});

test("2 approval focus waits until the Computer panel is visible", () => {
  const h = load();
  h.ready();
  const approval = h.el("computer-approval");
  h.el("daily-panel-computer").hidden = true;
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 0);
  h.el("daily-panel-computer").hidden = false;
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 1);
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 1);
});

test("2 resolving an approval moves focus to progress only when focus was inside the approval", () => {
  for (const inside of ["approval", "computer-approve", "computer-deny"]) {
    const h = load();
    h.ready();
    h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
    h.document.activeElement = h.el(inside === "approval" ? "computer-approval" : inside);
    h.ctrl.accept(h.task("running"), {replace: true});
    assert.equal(h.el("computer-progress").focusCalls, 1, inside);
    h.ctrl.changed();
    assert.equal(h.el("computer-progress").focusCalls, 1, `${inside} once only`);
  }
  const h = load();
  h.ready();
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  h.document.activeElement = h.el("computer-text");
  h.ctrl.accept(h.task("running"), {replace: true});
  assert.equal(h.el("computer-progress").focusCalls, 0, "focus elsewhere is left alone");
  assert.equal(h.document.activeElement, h.el("computer-text"));
});

test("3 idle, success and unverified outcomes have distinct tone and text", () => {
  const h = load();
  h.ready();
  h.ctrl.changed();
  assert.equal(h.el("computer-progress").dataset.state, "idle");
  assert.equal(h.el("computer-status").dataset.state, "idle");
  assert.match(h.el("computer-progress").textContent, /No task yet/);
  const idleText = h.el("computer-progress").textContent;
  h.ctrl.accept(h.task("succeeded", {verification: "SUCCESS"}), {replace: true});
  assert.equal(h.el("computer-progress").dataset.state, "success");
  assert.equal(h.el("computer-status").dataset.state, "success");
  assert.match(h.el("computer-progress").textContent, /Finished and verified by readback/);
  assert.notEqual(h.el("computer-progress").textContent, idleText);
  h.ctrl.accept(h.task("succeeded", {verification: "NOT_VERIFIED"}), {replace: true});
  assert.equal(h.el("computer-progress").dataset.state, "attention");
  assert.equal(h.el("computer-status").dataset.state, "attention");
  assert.match(h.el("computer-progress").textContent, /not verified/);
});

test("a lock while a button has focus keeps focus on the approval card, then hands it to progress", () => {
  const h = load();
  h.ready();
  const approval = h.el("computer-approval"), progress = h.el("computer-progress");
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  assert.equal(approval.focusCalls, 1);
  h.document.activeElement = h.el("computer-approve");
  h.ctrl.busy = true;
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 2);
  h.ctrl.changed();
  h.ctrl.changed();
  assert.equal(approval.focusCalls, 2, "not again while busy");
  assert.equal(progress.focusCalls, 0);
  h.ctrl.accept(h.task("running"), {replace: true});
  assert.equal(progress.focusCalls, 1);
});

test("b disconnect while a button has focus moves focus to the approval card, not progress", () => {
  const h = load();
  h.ready();
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  h.document.activeElement = h.el("computer-deny");
  h.ctrl.connected = false;
  h.ctrl.changed();
  assert.equal(h.el("computer-approval").focusCalls, 2);
  assert.equal(h.el("computer-progress").focusCalls, 0);
  h.ctrl.changed();
  assert.equal(h.el("computer-approval").focusCalls, 2);
  assert.equal(h.el("computer-progress").focusCalls, 0);
});

test("c focus the user moved elsewhere during busy is never taken back", () => {
  const h = load();
  h.ready();
  h.ctrl.accept(h.task("awaiting_permission"), {replace: true});
  h.document.activeElement = h.el("computer-approve");
  h.ctrl.busy = true;
  h.ctrl.changed();
  assert.equal(h.el("computer-approval").focusCalls, 2);
  h.document.activeElement = h.el("computer-text");
  h.ctrl.accept(h.task("running"), {replace: true});
  assert.equal(h.el("computer-progress").focusCalls, 0);
  assert.equal(h.document.activeElement, h.el("computer-text"));
});

test("d a repeated identical validation error is written again so it is re-announced", async () => {
  const h = load();
  h.ready();
  h.el("computer-input-mode").value = "task";
  h.el("computer-text").value = "open the browser";
  const submit = h.el("computer-form").handlers.submit;
  assert.equal(typeof submit, "function", "form submit handler registered");
  const error = h.el("computer-input-error");
  let previous = h.count("computer-input-error.textContent"), first = "";
  for (let i = 0; i < 2; i += 1) {
    submit({preventDefault() {}});
    await Promise.resolve();
    assert.notEqual(error.textContent, "");
    if (i === 0) first = error.textContent; else assert.equal(error.textContent, first);
    assert.equal(error.hidden, false);
    const now = h.count("computer-input-error.textContent");
    assert.ok(now > previous, `submit ${i + 1} rewrote the error text`);
    previous = now;
  }
});

test("e an unverified finish says so in the status line; a verified one does not", () => {
  const h = load();
  h.ready();
  h.ctrl.accept(h.task("succeeded", {verification: "NOT_VERIFIED"}), {replace: true});
  assert.match(h.el("computer-status").textContent, /not verified/);
  assert.match(h.el("computer-progress").textContent, /not verified/);
  h.ctrl.accept(h.task("succeeded", {verification: "SUCCESS"}), {replace: true});
  assert.doesNotMatch(h.el("computer-status").textContent, /not verified/);
});

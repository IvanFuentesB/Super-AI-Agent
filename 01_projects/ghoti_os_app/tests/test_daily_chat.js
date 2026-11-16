"use strict";
// Protocol fixtures only. These tests never start Hermes or grant live permission.
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const source = path.join(__dirname, "../dashboard_app/static/chat.js");
const MODEL = "openai-codex:gpt-6-astra";
const bootstrap = () => ({schema: "ghoti_chat_state/1", available: true, reason: null,
  csrf_token: "fixture-csrf", models: [{id: MODEL, label: "Astra"}], sessions: [], reasoning_effort: "max"});
function harness(replies) {
  assert.ok(fs.existsSync(source), "The daily chat protocol client must exist");
  const {ChatClient} = require(source);
  const calls = [];
  const client = new ChatClient({fetch: async (url, options = {}) => {
    calls.push({url, ...options, body: options.body ? JSON.parse(options.body) : undefined});
    const value = replies.shift();
    if (value instanceof Error) throw value;
    assert.ok(value, `Unexpected request ${url}`);
    return {ok: true, status: 200, json: async () => value};
  }, makeId: () => `fixture-request-${calls.length}`});
  return {client, calls};
}
const session = () => ({session_id: "fixture-session", model_id: MODEL, reasoning_effort: "max", state: "idle"});
const accepted = () => ({session_id: "fixture-session", request_id: "fixture-request-2", state: "running"});

test("bootstrap is read-only; send creates one session and one CSRF-bound prompt", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted()]);
  await client.bootstrap();
  assert.equal(calls.length, 1);
  assert.equal(client.state.phase, "ready");
  await client.send("An explicitly submitted task");
  assert.equal(calls.length, 3);
  assert.equal(calls[1].url, "/api/runtime/chat/sessions");
  assert.deepEqual(calls[1].body, {request_id: "fixture-request-1", model_id: MODEL});
  assert.equal(calls[2].body.text, "An explicitly submitted task");
  for (const call of calls.slice(1)) {
    assert.equal(call.headers["X-Ghoti-CSRF"], "fixture-csrf");
    assert.equal(call.headers["Content-Type"], "application/json");
    assert.equal(call.cache, "no-store");
  }
  assert.equal(client.state.phase, "running");
  assert.equal(client.state.sessionId, "fixture-session");
});

test("unavailable bootstrap is honest and cannot send", async () => {
  const value = {...bootstrap(), available: false, reason: "ACP is not configured"};
  const {client, calls} = harness([value]);
  client.state.modelId = MODEL; // A previous observation must not remain verified.
  client.state.effort = "max";
  await client.bootstrap();
  assert.equal(client.state.phase, "unavailable");
  assert.equal(client.state.reason, `Chat unavailable · ${value.reason}. No message was sent.`);
  assert.equal(client.state.modelId, null);
  assert.equal(client.state.effort, null);
  await client.send("must not run");
  assert.equal(calls.length, 1);
});

function batch(events, state = "running", after = 0, has_more = false) {
  return {session_id: "fixture-session", events: events.map(([type, payload], index) =>
    ({seq: after + index + 1, type, payload})), next_seq: after + events.length, has_more, state};
}
const permission = (request_id = "fixture-permission") => ["permission", {request_id,
  title: "Read a fixture", description: "<img src=x onerror=evil()> is text, not markup",
  options: [{id: "allow_once", label: "Once"}, {id: "deny", label: "Deny"}]}];

test("events stream text and exact permissions; only explicit offered choices can be sent once", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted(), batch([
    ["assistant_delta", {text: "A response <script>not executed</script>"}],
    ["tool_update", {tool_call_id: "fixture-tool", title: "Read fixture", status: "pending"}], permission()], "awaiting_permission"),
    {accepted: true}, batch([["assistant_delta", {text: " continued"}],
      ["turn_complete", {stop_reason: "end_turn"}]], "idle", 3)]);
  await client.bootstrap();
  await client.send("fixture task");
  await client.poll();
  assert.equal(calls.length, 4, "Polling must not auto-approve");
  assert.equal(client.state.phase, "permission");
  assert.equal(client.state.messages[1].text, "A response <script>not executed</script>");
  assert.equal(client.state.permissions[0].request_id, "fixture-permission");
  assert.equal(client.state.tools[0].status, "pending");
  for (const [id, choice] of [["unknown", "deny"], ["fixture-permission", "allow_always"]]) {
    assert.equal(await client.approve(id, choice), false);
  }
  assert.equal(calls.length, 4);
  assert.equal(await client.approve("fixture-permission", "allow_once"), true);
  assert.equal(await client.approve("fixture-permission", "allow_once"), false);
  assert.deepEqual(calls[4].body, {request_id: "fixture-permission", choice: "allow_once"});
  assert.equal(calls[4].headers["X-Ghoti-CSRF"], "fixture-csrf");
  await client.poll();
  assert.equal(calls[5].url, "/api/runtime/chat/sessions/fixture-session/events?after=3");
  assert.equal(client.state.phase, "complete");
  assert.equal(client.state.messages[1].text, "A response <script>not executed</script> continued");
  assert.equal(client.state.permissions.length, 0);
});

test("cancel acknowledgement is not terminal; wait for idle and cancelled event", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted(),
    {session_id: "fixture-session", state: "cancelling"}, batch([], "cancelling"),
    batch([["turn_complete", {stop_reason: "cancelled"}]], "idle")]);
  await client.bootstrap(); await client.send("fixture");
  assert.equal(await client.cancel(), true);
  assert.equal(client.state.phase, "cancelling");
  await client.poll();
  assert.equal(client.state.phase, "cancelling");
  await client.poll();
  assert.equal(client.state.phase, "cancelled");
  assert.match(client.state.reason, /prior|earlier/i);
  assert.equal(calls.filter(c => c.url.endsWith("/cancel")).length, 1);
});

test("permission events from history or an expired remote state never enable approval", async () => {
  for (const remote of ["running", "idle", "failed", "interrupted", "closed", "unknown"]) {
    const {client, calls} = harness([bootstrap(), session(), accepted(), batch([permission()], remote),
      {session_id: "fixture-session", state: "cancelling"}]);
    await client.bootstrap(); await client.send("fixture"); await client.poll();
    assert.notEqual(client.state.phase, "permission", remote);
    assert.equal(await client.approve("fixture-permission", "allow_once"), false);
    assert.ok(calls.every(c => !c.url.endsWith("/approval")));
  }
});

test("a completed event cannot erase an error; unknown stop reasons are not success", async () => {
  for (const [events, expected] of [
    [[["error", {code: "fixture_error", message: "failed"}], ["turn_complete", {stop_reason: "end_turn"}]], "failed"],
    [[["turn_complete", {stop_reason: "not_cancelled_but_not_success"}]], "ended"],
  ]) {
    const {client} = harness([bootstrap(), session(), accepted(), batch(events, "idle")]);
    await client.bootstrap(); await client.send("fixture"); await client.poll();
    assert.equal(client.state.phase, expected);
  }
});

test("pagination drains before permissions; terminal events remove historical requests", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted(), batch([permission()], "awaiting_permission", 0, true),
    batch([["turn_complete", {stop_reason: "end_turn"}]], "idle", 1)]);
  await client.bootstrap(); await client.send("fixture"); await client.poll();
  assert.equal(client.state.phase, "syncing");
  assert.equal(await client.approve("fixture-permission", "allow_once"), false);
  await client.poll();
  assert.equal(client.state.phase, "complete");
  assert.equal(client.state.permissions.length, 0);
  assert.equal(calls.length, 5);
});

test("disconnect clears permissions and requests a safety cancellation, never a prompt retry", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted(), batch([permission()], "awaiting_permission"),
    new Error("fixture network failure"), {session_id: "fixture-session", state: "cancelling"}]);
  await client.bootstrap(); await client.send("fixture"); await client.poll(); await client.poll();
  assert.equal(client.state.phase, "disconnected");
  assert.equal(client.state.permissions.length, 0);
  await client.send("must not replay"); await client.bootstrap(); await client.poll();
  assert.equal(calls.filter(c => c.url.endsWith("/prompt")).length, 1);
  assert.equal(calls.filter(c => c.url.endsWith("/cancel")).length, 1);
});

test("reused permission ID and permanent consent options fail closed", async () => {
  for (const bad of [permission(), ["permission", {...permission("other")[1], options: [{id: "allow_always", label: "Always"}]}]]) {
    const {client} = harness([bootstrap(), session(), accepted(), batch([permission()], "awaiting_permission"),
      batch([bad], "awaiting_permission", 1), {session_id: "fixture-session", state: "cancelling"}]);
    await client.bootstrap(); await client.send("fixture"); await client.poll(); await client.poll();
    assert.equal(client.state.phase, "disconnected");
    assert.equal(client.state.permissions.length, 0);
  }
});

test("cancellation wins a race against a late approval response", async () => {
  const {client} = harness([bootstrap(), session(), accepted(), batch([permission()], "awaiting_permission")]);
  await client.bootstrap(); await client.send("fixture"); await client.poll();
  let resolveApproval;
  client.fetch = async url => url.endsWith("/approval") ? new Promise(resolve => { resolveApproval = resolve; }) :
    {ok: true, json: async () => ({session_id: "fixture-session", state: "cancelling"})};
  const approving = client.approve("fixture-permission", "deny");
  await client.cancel();
  resolveApproval({ok: true, json: async () => ({accepted: true})});
  await approving;
  assert.equal(client.state.phase, "cancelling");
});

test("idle cancellation acknowledgement still drains buffered failure evidence", async () => {
  const {client} = harness([bootstrap(), session(), accepted(), {session_id: "fixture-session", state: "idle"},
    batch([["error", {code: "fixture_failure", message: "actual failure before cancel"}]], "idle")]);
  await client.bootstrap(); await client.send("fixture"); await client.cancel();
  assert.equal(client.state.phase, "cancelling");
  await client.poll();
  assert.equal(client.state.phase, "failed");
  assert.match(client.state.reason, /actual failure before cancel/);
});

test("late cancel response cannot replace an observed runtime failure", async () => {
  const {client} = harness([bootstrap(), session(), accepted()]);
  await client.bootstrap(); await client.send("fixture");
  let resolveCancel;
  client.fetch = async url => url.endsWith("/cancel") ? new Promise(resolve => {resolveCancel = resolve;}) :
    {ok: true, json: async () => batch([["error", {code: "fixture_failure", message: "failed before acknowledgement"}]], "failed")};
  const cancelling = client.cancel();
  await client.poll();
  assert.equal(client.state.phase, "failed");
  resolveCancel({ok: true, json: async () => ({session_id: "fixture-session", state: "idle"})});
  await cancelling;
  assert.equal(client.state.phase, "failed");
});

test("late prompt acknowledgement after cancel triggers another safety stop, not a prompt retry", async () => {
  const {client, calls} = harness([bootstrap(), session()]);
  await client.bootstrap();
  let resolvePrompt;
  let cancels = 0;
  const transport = client.fetch;
  client.fetch = async (url, options) => {
    if (url.endsWith("/prompt")) return new Promise(resolve => {resolvePrompt = resolve;});
    if (url.endsWith("/cancel")) {cancels++; return {ok: true, json: async () => ({session_id: "fixture-session", state: "idle"})};}
    return transport(url, options);
  };
  const sending = client.send("fixture");
  await new Promise(resolve => setImmediate(resolve));
  await client.cancel();
  resolvePrompt({ok: true, json: async () => accepted()});
  await sending;
  assert.equal(cancels, 2);
  assert.equal(client.state.phase, "disconnected");
  assert.equal(calls.filter(c => c.url.endsWith("/sessions")).length, 1);
});

test("page teardown uses a bounded CSRF-bearing keepalive cancellation", async () => {
  const {client, calls} = harness([bootstrap(), session(), accepted(), {session_id: "fixture-session", state: "cancelling"}]);
  await client.bootstrap(); await client.send("fixture");
  await client.disconnect("Page disconnected", {keepalive: true});
  assert.equal(calls.at(-1).keepalive, true);
  assert.equal(calls.at(-1).headers["X-Ghoti-CSRF"], "fixture-csrf");
  assert.deepEqual(Object.keys(calls.at(-1).body), ["request_id", "prompt_request_id"]);
  assert.equal(calls.at(-1).body.prompt_request_id, "fixture-request-2");
});

test("message validation matches character and escaped UTF-8 body limits without writes", async () => {
  const {promptError} = require(source);
  const {client, calls} = harness([bootstrap()]);
  await client.bootstrap();
  for (const text of ["", " ", " /command", "bad\0text", "\ud800", "x".repeat(12001), "界".repeat(6000), "\n".repeat(11999) + "x"]) {
    assert.notEqual(promptError(text), "");
    assert.equal(await client.send(text), false);
  }
  for (const text of ["A valid message", "A newline\nfollow-up", "Unicode: café 🌱", "x".repeat(12000)]) assert.equal(promptError(text), "");
  assert.equal(calls.length, 1);
});

test("read-only paginated history ignores permissions and never changes live state", async () => {
  const b = bootstrap();
  b.sessions = [{session_id: "fixture-session", state: "idle", model_id: MODEL}];
  const {client, calls} = harness([b,
    batch([["assistant_delta", {text: "Saved <script>text</script>"}], permission()], "idle", 0, true),
    batch([["turn_complete", {stop_reason: "end_turn"}], ["assistant_delta", {text: "Partial"}]], "idle", 2)]);
  await client.bootstrap();
  const before = JSON.stringify(client.state);
  const saved = await client.readHistory("fixture-session");
  assert.deepEqual(saved.replies, [{text: "Saved <script>text</script>", partial: false}, {text: "Partial", partial: true}]);
  assert.equal(JSON.stringify(client.state), before);
  assert.ok(calls.every(call => !call.method));
  assert.equal(calls.at(-1).url, "/api/runtime/chat/sessions/fixture-session/events?after=2");
  assert.equal(client.state.permissions.length, 0);
});

test("history fails closed on active sessions, malformed cursors and oversized text", async () => {
  for (const response of [batch([], "running"), {...batch([], "idle"), next_seq: 99},
    batch([], "idle", 0, true), batch([["assistant_delta", {text: "a".repeat(500001)}]], "idle"),
    {...batch([], "idle"), session_id: "wrong-session"}]) {
    const b = bootstrap();
    b.sessions = [{session_id: "fixture-session", state: "idle", model_id: MODEL}];
    const {client, calls} = harness([b, response]);
    await client.bootstrap();
    await assert.rejects(client.readHistory("fixture-session"));
    assert.equal(client.state.phase, "ready");
    assert.ok(calls.every(call => !call.method));
  }
  const b = bootstrap();
  b.sessions = [{session_id: "fixture-session", state: "awaiting_permission", model_id: MODEL}];
  const {client, calls} = harness([b]);
  await client.bootstrap();
  await assert.rejects(client.readHistory("fixture-session"));
  assert.equal(calls.length, 1);
});

test("failed history refresh clears stale sessions without changing active chat", async () => {
  const b = bootstrap();
  b.sessions = [{session_id: "fixture-session", state: "idle", model_id: MODEL}];
  const {client} = harness([b, new Error("fixture disconnected")]);
  await client.bootstrap();
  await assert.rejects(client.refreshSessions());
  assert.deepEqual(client.state.sessions, []);
  assert.equal(client.state.sessionsStatus, "unavailable");
  assert.equal(client.state.phase, "ready");
  await assert.rejects(client.readHistory("fixture-session"));
});

test("an old cancel acknowledgement cannot change a new turn", async () => {
  const {client} = harness([bootstrap(), session(), accepted()]);
  await client.bootstrap(); await client.send("turn A");
  let resolveCancel, requestCounter = 100;
  client.makeId = () => `fixture-request-${++requestCounter}`;
  client.fetch = async (url, options = {}) => {
    if (url.endsWith("/cancel")) return new Promise(resolve => {resolveCancel = resolve;});
    if (url.includes("/events")) return {ok: true, json: async () => batch([["turn_complete", {stop_reason: "end_turn"}]], "idle")};
    return {ok: true, json: async () => ({...accepted(), request_id: JSON.parse(options.body).request_id})};
  };
  const cancelling = client.cancel();
  await client.poll();
  assert.equal(client.state.phase, "complete");
  await client.send("turn B");
  assert.equal(client.state.phase, "running");
  resolveCancel({ok: true, json: async () => ({session_id: "fixture-session", state: "cancelling"})});
  await cancelling;
  assert.equal(client.state.phase, "running", "a delayed acknowledgement for A must not cancel B");
  assert.equal(client.state.messages.at(-1).text, "turn B");
});

test("mode stays local and idle-only; effort is unknown until matching verified policy", async () => {
  const policy = (mode, effort, request_id = "fixture-request-2") => ["policy", {request_id, mode, effort,
    model_id: MODEL, verified: true, source: "native_wire_preflight"}];
  const {client, calls} = harness([bootstrap(), session(), accepted(), batch([policy("fast", "low")]),
    batch([["turn_complete", {stop_reason: "end_turn"}]], "idle", 1),
    {session_id: "fixture-session", request_id: "fixture-request-5", state: "running"}]);
  await client.bootstrap();
  assert.equal(client.state.mode, "auto");
  assert.equal(client.state.effort, null, "bootstrap is not effective turn policy");
  assert.equal(client.setMode("fast"), true);
  assert.equal(client.setMode("unrecognized"), false);
  assert.equal(calls.length, 1, "mode selection has no network or storage side effect");
  await client.send("fixture");
  assert.equal(calls[2].body.mode, "fast");
  assert.equal(client.state.effort, null);
  assert.equal(client.setMode("deep"), false);
  await client.poll();
  assert.equal(client.state.effort, "low");
  await client.poll();
  assert.equal(client.setMode("auto"), true);
  assert.equal(client.state.effort, null);
  await client.send("second");
  assert.equal(client.state.mode, "auto");
  assert.equal(calls.at(-1).body.mode, "auto");
});

test("wrong-turn or unverified effort never becomes effective policy", async () => {
  for (const override of [{request_id: "old-turn"}, {effort: "max"}, {mode: "deep"}, {verified: false},
    {model_id: "other"}, {source: "requested"}]) {
    const {client} = harness([bootstrap(), session(), accepted(), batch([["policy", {
      request_id: "fixture-request-2", mode: "auto", effort: "medium", model_id: MODEL,
      verified: true, source: "native_wire_preflight", ...override}]]), {session_id: "fixture-session", state: "cancelling"}]);
    await client.bootstrap(); await client.send("fixture"); await client.poll();
    assert.equal(client.state.effort, null);
    assert.equal(client.state.phase, "disconnected");
  }
});

test("timing and first rendered text stay bound to the current prompt", async () => {
  const {client} = harness([bootstrap(), {session_id: "fixture-session", model_id: "openai-codex:gpt-6-astra", reasoning_effort: "max", state: "idle"}, accepted()]);
  await client.bootstrap(); await client.send("fixture");
  client.applyEvent({type:"timing",payload:{request_id:client.promptRequest,phase:"provider_request",elapsed_ms:20,attempt:1}});
  client.applyEvent({type:"assistant_delta",payload:{text:"fixture response"}});
  assert.equal(client.noteVisibleText("retired-request"),false);
  assert.equal(client.state.timings.first_visible_text_ms,undefined);
  assert.equal(client.noteVisibleText(client.promptRequest),true);
  assert.ok(Number.isFinite(client.state.timings.first_visible_text_ms));
  assert.equal(client.state.timings.server.provider_request,20);
});

test("remote failed state preserves the actual failure detail", async () => {
  const {client} = harness([bootstrap(), session(), accepted(),
    batch([["error", {code: "transport_disconnected", message: "Actual failure detail"}]], "failed")]);
  await client.bootstrap(); await client.send("fixture"); await client.poll();
  assert.equal(client.state.phase, "failed");
  assert.equal(client.state.reason, "transport_disconnected: Actual failure detail");
});

test("late failed cancellation cannot disconnect or cancel the next turn", async () => {
  const {client}=harness([bootstrap(),{session_id:"fixture-session",model_id:"openai-codex:gpt-6-astra",reasoning_effort:"max",state:"idle"},accepted()]);
  await client.bootstrap();
  assert.equal(await client.send("First"),true);
  let rejectCancel,requests=100,cancelCount=0;
  client.makeId=()=>`fixture-request-${++requests}`;
  const response=data=>({ok:true,status:200,json:async()=>data});
  const delayed=new Promise((resolve,reject)=>{rejectCancel=reject;});
  client.fetch=async(url,options={})=>{
    if(url.endsWith("/cancel")){cancelCount++;return delayed;}
    if(url.includes("/events?"))return response(batch([["turn_complete",{stop_reason:"end_turn"}]],"idle"));
    if(url.endsWith("/prompt"))return response({...accepted(),request_id:JSON.parse(options.body).request_id});
    throw new Error("unexpected fixture path");
  };
  const oldCancel=client.cancel();await client.poll();
  assert.equal(await client.send("Second"),true);
  rejectCancel(new Error("Old cancellation request failed"));await oldCancel;
  assert.equal(client.state.phase,"running");assert.equal(cancelCount,1);
});

test("saved timing events remain read-only and do not break history", async () => {
  const {client,calls}=harness([batch([
    ["timing",{request_id:"fixture-prompt",phase:"queue",elapsed_ms:0,count:1}],
    ["assistant_delta",{text:"saved answer"}],
    ["turn_complete",{stop_reason:"end_turn"}]],"idle")]);
  client.state.sessions=[{session_id:"fixture-session",state:"idle"}];
  const history=await client.readHistory("fixture-session");
  assert.equal(history.replies[0].text,"saved answer");
  assert.ok(calls.every(c=>!c.method));assert.equal(client.state.sessionId,null);
});



test("HTTP errors disclose only known safe codes, never arbitrary error bodies", async () => {
  const {client}=harness([]);
  for(const body of [null, {}, {error:"manual_approvals_required"}, {error:true,code:"private failure detail"},
    {error:true,code:{toString:"manual_approvals_required"}}, {error:true,code:"other",message:"private failure detail"}]) {
    client.fetch=async()=>({ok:false,status:503,json:async()=>body});
    await assert.rejects(client.request(""),{message:"Local chat request failed (HTTP 503)"});
  }
  client.fetch=async()=>({ok:false,status:503,json:async()=>{throw new Error("private parse detail");}});
  await assert.rejects(client.request(""),{message:"Local chat request failed (HTTP 503)"});
  client.fetch=async()=>({ok:false,status:503,json:async()=>({error:true,code:"inherited_approval_bypass",message:"private failure detail"})});
  await assert.rejects(client.request(""),{message:"Native chat refused an inherited approval bypass"});
});

test("native manual-policy failure is actionable without replaying a prompt", async () => {
  const {client}=harness([bootstrap()]);await client.bootstrap();let calls=0;
  client.fetch=async()=>{calls++;return {ok:false,status:503,json:async()=>({error:true,code:"manual_approvals_required"})};};
  assert.equal(await client.send("fixture"),false);assert.equal(calls,1);
  assert.match(client.state.reason,/Manual approvals/);
  assert.match(client.state.reason,/No prompt was submitted/);
  assert.doesNotMatch(client.state.reason,/Submission outcome unknown/);
  assert.equal(client.state.messages.length,0);
  assert.equal(await client.send("must not replay"),false);assert.equal(calls,1);
});

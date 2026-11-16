"use strict";
// Frozen ghoti_chat_state/1 client. No browser persistence, retries or fallback models.
(() => {
  const MODEL = "openai-codex:gpt-6-astra";
  const MODES = Object.freeze({fast: "low", auto: "medium", deep: "max"});
  const SESSION_STATES = new Set(["idle", "running", "awaiting_permission", "cancelling", "failed", "interrupted", "closed"]);
  const idOK = value => typeof value === "string" && /^[A-Za-z0-9_-]{1,128}$/.test(value);
  const requireThat = (condition, message) => { if (!condition) throw new Error(message); };
  function promptError(text) {
    if (typeof text !== "string" || !text.trim()) return "Write a message first.";
    if (text.length > 12000) return "Keep your message under 12,000 characters.";
    if (text.includes("\0") || /[\uD800-\uDFFF]/u.test(text)) return "Your message contains unsupported characters.";
    if (text.trimStart().startsWith("/")) return "Slash commands aren’t supported. Describe your task in plain text.";
    // JSON escaping and multibyte text count toward the server's 16 KiB body limit.
    if (new TextEncoder().encode(JSON.stringify({request_id: "x".repeat(96), text, mode: "auto"})).length > 16384) {
      return "This message is too large to send. Shorten it and try again.";
    }
    return "";
  }
  function sessionsFrom(data) {
    requireThat(data.schema === "ghoti_chat_state/1" && Array.isArray(data.sessions) && data.sessions.length <= 64,
      "Invalid session list");
    requireThat(new Set(data.sessions.map(s => s.session_id)).size === data.sessions.length, "Duplicate session identity");
    return data.sessions.map(s => {
      requireThat(idOK(s.session_id) && SESSION_STATES.has(s.state) && typeof s.model_id === "string", "Invalid session identity");
      return {session_id: s.session_id, state: s.state, model_id: s.model_id};
    });
  }
  class ChatClient {
    constructor({fetch: transport = globalThis.fetch.bind(globalThis), onChange = () => {},
      makeId = () => globalThis.crypto.randomUUID()} = {}) {
      this.fetch = transport;
      this.onChange = onChange;
      this.makeId = makeId;
      this.clock = () => globalThis.performance?.now() ?? Date.now();
      this.turnStarted = null;
      this.csrf = null;
      this.polling = false;
      this.actionPending = false;
      this.submitting = false;
      this.epoch = 0;
      this.promptRequest = null;
      this.seenPermissions = new Set();
      this.state = {phase: "loading", reason: "Checking local chat…", available: false,
        sessionId: null, modelId: null, mode: "auto", effort: null, sessions: [], sessionsStatus: "loading", messages: [],
        tools: [], permissions: [], cursor: 0, hasMore: false, timings: {server: {}}};
    }
    changed() { this.onChange(this.state); }
    setMode(mode) {
      if (!Object.hasOwn(MODES, mode) || this.submitting || this.actionPending ||
          !["ready", "complete", "cancelled", "ended"].includes(this.state.phase)) return false;
      if (this.state.mode !== mode) {
        this.state.mode = mode;
        this.state.effort = null;
        this.changed();
      }
      return true;
    }
    noteVisibleText(requestId = this.promptRequest) {
      if (requestId !== this.promptRequest || this.turnStarted === null ||
          this.state.timings.first_visible_text_ms !== undefined ||
          this.state.messages.at(-1)?.role !== "assistant" || !this.state.messages.at(-1).text.trim()) return false;
      this.state.timings.first_visible_text_ms = Math.max(0, this.clock() - this.turnStarted);
      this.state.timings.browser_clock = "milliseconds since prompt HTTP send; rendered visible frame";
      this.changed();
      return true;
    }
    async poll() {
      if (this.polling || this.actionPending || !["running", "permission", "syncing", "cancelling"].includes(this.state.phase)) return;
      this.polling = true;
      const epoch = this.epoch;
      try {
        const data = await this.request(`/sessions/${this.state.sessionId}/events?after=${this.state.cursor}`);
        if (epoch !== this.epoch) return;
        requireThat(data.session_id === this.state.sessionId && Array.isArray(data.events) &&
          data.events.length <= 1000 && typeof data.has_more === "boolean" && SESSION_STATES.has(data.state),
        "Invalid event envelope");
        let cursor = this.state.cursor;
        const pendingIds = new Set(this.seenPermissions);
        for (const event of data.events) {
          requireThat(Number.isSafeInteger(event.seq) && event.seq > cursor && event.payload &&
            typeof event.payload === "object", "Invalid or repeated event sequence");
          cursor = event.seq;
          const p = event.payload;
          switch (event.type) {
            case "assistant_delta": requireThat(typeof p.text === "string", "Invalid assistant text"); break;
            case "tool_update": requireThat(idOK(p.tool_call_id) && typeof p.title === "string" &&
              typeof p.status === "string", "Invalid tool update"); break;
            case "permission":
              requireThat(idOK(p.request_id) && !pendingIds.has(p.request_id) && typeof p.title === "string" &&
                typeof p.description === "string" && Array.isArray(p.options) && p.options.length > 0 &&
                p.options.length <= 2 && p.options.every(o => ["allow_once", "deny"].includes(o.id) && typeof o.label === "string") &&
                new Set(p.options.map(o => o.id)).size === p.options.length && p.options.some(o => o.id === "deny"),
              "Invalid or replayed permission request");
              pendingIds.add(p.request_id);
              break;
            case "timing":
              requireThat(p.request_id === this.promptRequest &&
                ["queue", "context_prepare", "provider_request", "first_token", "completion"].includes(p.phase) &&
                Number.isFinite(p.elapsed_ms) && p.elapsed_ms >= 0 && p.elapsed_ms <= 360000 &&
                Number.isSafeInteger(p.attempt) && p.attempt > 0 && p.attempt <= 64, "Invalid turn timing");
              break;
            case "policy":
              requireThat(p.request_id === this.promptRequest && p.mode === this.state.mode &&
                p.effort === MODES[this.state.mode] && p.model_id === MODEL && p.verified === true &&
                p.source === "native_wire_preflight", "Unverified effective policy");
              break;
            case "turn_complete": requireThat(typeof p.stop_reason === "string", "Invalid completion"); break;
            case "error": requireThat(typeof p.code === "string" && typeof p.message === "string", "Invalid error"); break;
            default: throw new Error("Unknown event type; controls locked");
          }
        }
        requireThat(data.next_seq === cursor && (!data.has_more || data.events.length > 0), "Invalid event cursor");
        for (const event of data.events) this.applyEvent(event);
        this.state.cursor = cursor;
        this.state.hasMore = data.has_more;
        const remote = data.state;
        if (["failed", "interrupted", "closed"].includes(remote)) {
          if (this.terminalPhase !== "failed") this.state.reason = `Session ${remote}. No actions will be replayed.`;
          this.terminalPhase = "failed";
        } else if (remote === "idle" && this.cancelRequested && !this.terminalPhase) {
          this.terminalPhase = "cancelled";
          this.state.reason = "Cancelled. Earlier tool actions may already have happened.";
        }
        if (this.terminalPhase) {
          this.state.permissions = [];
          this.state.phase = this.submitting || data.has_more || !["idle", "failed", "interrupted", "closed"].includes(remote) ? "syncing" : this.terminalPhase;
        } else if (!data.has_more && remote === "idle") {
          throw new Error("Stream ended without a turn_complete event");
        } else {
          if (remote !== "awaiting_permission") this.state.permissions = [];
          requireThat(data.has_more || remote !== "awaiting_permission" || this.state.permissions.length === 1,
            "No unique live permission request");
          this.state.phase = data.has_more ? "syncing" : this.cancelRequested || remote === "cancelling" ? "cancelling" :
            remote === "awaiting_permission" ? "permission" : "running";
          this.state.reason = this.state.phase === "permission" ? "Your approval is required" : this.state.phase === "cancelling" ?
            "Cancellation pending · earlier actions may already have happened" : "Running · receiving runtime events";
        }
        this.lastPollAt = Date.now();
        this.changed();
      } catch (error) {
        if (epoch === this.epoch) await this.disconnect(error.message);
      } finally { this.polling = false; }
    }
    applyEvent({type, payload: p}) {
      if (type === "assistant_delta") {
        let message = this.state.messages.at(-1);
        if (message?.role !== "assistant") {
          message = {role: "assistant", text: ""};
          this.state.messages.push(message);
        }
        requireThat(message.text.length + p.text.length <= 500000, "Response exceeds the display limit");
        message.text += p.text;
      } else if (type === "tool_update") {
        const index = this.state.tools.findIndex(t => t.tool_call_id === p.tool_call_id);
        if (index < 0) this.state.tools.push({...p});
        else this.state.tools[index] = {...p};
      } else if (type === "permission") {
        this.seenPermissions.add(p.request_id);
        this.state.permissions.push({...p});
      } else if (type === "timing") {
        if (this.state.timings.server[p.phase] === undefined) this.state.timings.server[p.phase] = p.elapsed_ms;
        if (p.phase === "provider_request") this.state.timings.provider_request_operations = p.attempt;
      } else if (type === "policy") {
        this.state.effort = p.effort;
      } else if (type === "turn_complete") {
        if (this.terminalPhase !== "failed") {
          this.terminalPhase = p.stop_reason === "cancelled" ? "cancelled" : p.stop_reason === "end_turn" ? "complete" : "ended";
          this.state.reason = `Turn ended: ${p.stop_reason}. Earlier tool actions may have happened; task correctness is not established.`;
        }
      } else if (type === "error") {
        this.terminalPhase = "failed";
        this.state.reason = `${p.code}: ${p.message}`;
      }
    }
    async approve(requestId, choice) {
      const permission = this.state.permissions.find(p => p.request_id === requestId);
      if (this.actionPending || this.state.phase !== "permission" || !permission ||
        !permission.options.some(o => o.id === choice)) return false;
      if (Date.now() - this.lastPollAt > 10000) {
        await this.disconnect("Permission view expired");
        return false;
      }
      this.actionPending = true;
      this.epoch += 1;
      const epoch = this.epoch;
      this.state.permissions = this.state.permissions.filter(p => p.request_id !== requestId);
      this.state.phase = "approving";
      this.changed();
      try {
        const result = await this.request(`/sessions/${this.state.sessionId}/approval`, {request_id: requestId, choice});
        if (epoch !== this.epoch) return false;
        requireThat(result.accepted === true, "Permission rejected or expired");
        this.state.phase = this.state.permissions.length ? "permission" : "running";
        this.state.reason = choice === "deny" ? "Denied · waiting for runtime" : "Allowed once · waiting for runtime";
        return true;
      } catch (error) {
        if (epoch === this.epoch) await this.disconnect(error.message);
        return false;
      } finally { this.actionPending = false; this.changed(); }
    }
    async cancel() {
      if (!this.state.sessionId || this.state.phase === "cancelling") return false;
      this.epoch += 1;
      const epoch = this.epoch;
      this.cancelRequested = true;
      this.state.permissions = [];
      this.state.phase = "cancelling";
      this.state.reason = "Cancellation requested; awaiting confirmation";
      this.changed();
      try {
        const result = await this.request(`/sessions/${this.state.sessionId}/cancel`, {request_id: this.makeId(), prompt_request_id: this.promptRequest});
        if (epoch !== this.epoch || this.terminalPhase === "failed") return false;
        requireThat(result.session_id === this.state.sessionId && ["idle", "cancelling"].includes(result.state),
          "Cancellation is not confirmed");
        // Even an idle acknowledgement can have unread final events or errors.
        this.state.phase = "cancelling";
        this.state.reason = "Cancellation acknowledged · reading final evidence. Earlier actions may already have happened.";
        return true;
      } catch (error) {
        if (epoch === this.epoch && this.terminalPhase !== "failed") {
          this.state.phase = "disconnected";
          this.state.reason = `${error.message}. Cancellation unconfirmed; inspect runtime before starting again.`;
        }
        return false;
      } finally { this.changed(); }
    }
    async disconnect(reason = "Connection lost", {keepalive = false} = {}) {
      this.epoch += 1;
      this.state.permissions = [];
      this.state.phase = "disconnected";
      this.state.reason = `${reason}. Controls locked; nothing will be replayed.`;
      this.changed();
      // A safety stop is not a retry of the task or a grant of permission.
      if (this.state.sessionId) {
        try {
          const result = await this.request(`/sessions/${this.state.sessionId}/cancel`, {request_id: this.makeId(), prompt_request_id: this.promptRequest}, {keepalive});
          this.state.reason += result.session_id === this.state.sessionId && result.state === "idle" ?
            " Worker reported idle; final evidence not read, prior actions may have happened." : result.session_id === this.state.sessionId && result.state === "cancelling" ?
              " Safety cancellation pending; prior actions may have happened." : " Safety cancellation unconfirmed.";
        } catch (_) { this.state.reason += " Safety cancellation unconfirmed."; }
        this.changed();
      }
    }
    async request(path, body, {keepalive = false} = {}) {
      const options = {cache: "no-store", credentials: "same-origin", redirect: "error",
        signal: AbortSignal.timeout(30000), keepalive};
      if (body !== undefined) {
        requireThat(this.csrf, "No verified CSRF bootstrap");
        options.method = "POST";
        options.headers = {"Content-Type": "application/json", "X-Ghoti-CSRF": this.csrf};
        options.body = JSON.stringify(body);
      }
      const response = await this.fetch(`/api/runtime/chat${path}`, options);
      if (!response.ok) {
        let detail = "";
        try {
          const error = await response.json();
          if (error.code === "manual_approvals_required") detail = "Native chat requires Manual approvals in Hermes";
          else if (error.code === "inherited_approval_bypass") detail = "Native chat refused an inherited approval bypass";
        } catch (_) { /* Do not disclose arbitrary error bodies. */ }
        throw new Error(detail || `Local chat request failed (HTTP ${response.status})`);
      }
      return response.json();
    }
    async bootstrap() {
      if (this.state.sessionId || ["creating", "submitting", "running"].includes(this.state.phase)) return;
      this.state.phase = "loading";
      this.state.sessions = [];
      this.state.sessionsStatus = "unavailable";
      this.changed();
      try {
        const data = await this.request("");
        requireThat(data.schema === "ghoti_chat_state/1" && typeof data.available === "boolean",
          "Unrecognized local chat response");
        this.state.sessions = sessionsFrom(data);
        this.state.sessionsStatus = "ready";
        if (!data.available) throw new Error(typeof data.reason === "string" ? data.reason : "Local chat unavailable");
        requireThat(typeof data.csrf_token === "string" && data.csrf_token.length > 0,
          "Local chat did not provide a CSRF nonce");
        requireThat(Array.isArray(data.models) && data.models.some(m => m.id === MODEL) && data.reasoning_effort === "max",
          "Required Astra route and legacy default are not available");
        this.csrf = data.csrf_token;
        Object.assign(this.state, {phase: "ready", available: true, modelId: MODEL, effort: null,
          reason: "Local bridge connected · native policy is checked before sending"});
      } catch (error) {
        this.csrf = null;
        Object.assign(this.state, {phase: "unavailable", available: false, modelId: null, effort: null,
          reason: `Chat unavailable · ${error.message}. No message was sent.`});
      }
      this.changed();
    }
    async refreshSessions() {
      try {
        this.state.sessions = sessionsFrom(await this.request(""));
        this.state.sessionsStatus = "ready";
        return this.state.sessions;
      } catch (error) {
        this.state.sessions = [];
        this.state.sessionsStatus = "unavailable";
        throw error;
      } finally { this.changed(); }
    }
    async readHistory(sessionId) {
      const saved = this.state.sessions.find(s => s.session_id === sessionId);
      requireThat(saved && ["idle", "failed", "interrupted", "closed"].includes(saved.state),
        "Live conversations cannot be opened as history");
      // Historical events are data only. Never pass them to applyEvent/approve/send.
      let cursor = 0, size = 0, count = 0, current = "", failed = false;
      const replies = [];
      for (let page = 0; page < 83; page += 1) {
        const data = await this.request(`/sessions/${sessionId}/events?after=${cursor}`);
        requireThat(data.session_id === sessionId && Array.isArray(data.events) && data.events.length <= 100 &&
          typeof data.has_more === "boolean" && ["idle", "failed", "interrupted", "closed"].includes(data.state),
        "Saved conversation changed or is unavailable; refresh the list");
        for (const event of data.events) {
          requireThat(Number.isSafeInteger(event.seq) && event.seq > cursor && event.payload &&
            typeof event.payload === "object", "Invalid history sequence");
          cursor = event.seq;
          count += 1;
          if (event.type === "assistant_delta") {
            requireThat(typeof event.payload.text === "string", "Invalid saved reply");
            size += event.payload.text.length;
            current += event.payload.text;
          } else if (event.type === "turn_complete") {
            if (current) replies.push({text: current, partial: failed || event.payload.stop_reason !== "end_turn"});
            current = "";
            failed = false;
          } else if (event.type === "error") failed = true;
          else requireThat(["permission", "tool_update", "policy", "timing"].includes(event.type), "Unknown history event");
          requireThat(size <= 500000 && count <= 8192, "History exceeds display limit");
        }
        requireThat(data.next_seq === cursor && (!data.has_more || data.events.length > 0), "Invalid history cursor");
        if (!data.has_more) {
          if (current) replies.push({text: current, partial: true});
          return {replies, state: data.state};
        }
      }
      throw new Error("History exceeds page limit");
    }
    async send(text) {
      if (!this.state.available || !["ready", "complete", "cancelled", "ended"].includes(this.state.phase)) return false;
      if (promptError(text)) return false;
      this.state.phase = this.state.sessionId ? "submitting" : "creating";
      this.terminalPhase = null;
      this.cancelRequested = false;
      this.state.effort = null;
      this.submitting = true;
      const epoch = ++this.epoch;
      this.state.reason = "Submitting once; no automatic retries";
      this.changed();
      try {
        if (!this.state.sessionId) {
          const session = await this.request("/sessions", {request_id: this.makeId(), model_id: MODEL});
          requireThat(idOK(session.session_id), "Invalid session identity");
          // Retain the actual ID even if model verification fails, for explicit cancellation.
          this.state.sessionId = session.session_id;
          if (epoch !== this.epoch) { await this.disconnect("Session creation finished after disconnect"); return false; }
          requireThat(session.model_id === MODEL && session.reasoning_effort === "max" && session.state === "idle", "Session model/state verification failed");
          this.state.phase = "submitting";
        }
        const requestId = this.makeId();
        this.promptRequest = requestId;
        this.turnStarted = this.clock();
        this.state.timings = {server: {}, server_clock: "milliseconds since runtime admission request", first_token_definition: "first nonempty native streamed text chunk, not hidden reasoning"};
        const result = await this.request(`/sessions/${this.state.sessionId}/prompt`, {request_id: requestId, text, mode: this.state.mode});
        if (epoch !== this.epoch) { await this.disconnect("Prompt settled after a stop; outcome uncertain"); return false; }
        requireThat(result.session_id === this.state.sessionId && result.request_id === requestId && result.state === "running",
          "Prompt acknowledgement did not match the submitted request");
        this.state.messages.push({role: "user", text});
        Object.assign(this.state, {phase: "running", reason: "Running · waiting for runtime events"});
        this.changed();
        return true;
      } catch (error) {
        await this.disconnect(`${error.message}${this.state.sessionId ? ". Submission outcome unknown" : ". No prompt was submitted"}`);
        return false;
      } finally { this.submitting = false; }
    }
  }
  if (typeof module !== "undefined" && module.exports) module.exports = {ChatClient, promptError};
  else globalThis.GhotiChat = {ChatClient, promptError};
})();

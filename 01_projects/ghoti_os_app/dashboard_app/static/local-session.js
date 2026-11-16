/* Local-only identity for Computer. No credentials are stored in browser storage. */
(function (root) {
  "use strict";
  class LocalConnection {
    constructor(options = {}) {
      this.fetch = options.fetch || root.fetch.bind(root);
      this.location = options.location || root.location;
      this.history = options.history || root.history;
      this.authenticated = false;
      this.csrf = null;
      this.reason = "Open Ghoti using its installed shortcut to connect local control.";
    }
    async bootstrap() {
      if (this.location.protocol !== "http:" || this.location.hostname !== "127.0.0.1") return this;
      const url = new URL(this.location.href);
      const params = new URLSearchParams(url.hash.slice(1));
      let ticket = params.get("ghoti_local");
      if (ticket !== null) this.history.replaceState(null, "", url.pathname + "#chat");
      const options = {credentials: "same-origin", cache: "no-store", redirect: "error", signal: AbortSignal.timeout(10000), headers: {"Content-Type": "application/json"}};
      if (ticket !== null) { options.method = "POST"; options.body = JSON.stringify({ticket}); }
      ticket = null;
      try {
        const response = await this.fetch("/api/runtime/local-session", options);
        const state = await response.json();
        this.authenticated = response.ok && state.authenticated === true && typeof state.csrf_token === "string";
        this.csrf = this.authenticated ? state.csrf_token : null;
        this.reason = this.authenticated ? "Authenticated local session" : "Open Ghoti using its installed shortcut. An expired launch link cannot be reused.";
      } catch (_) {
        this.authenticated = false; this.csrf = null;
        this.reason = "Local service disconnected. Reopen Ghoti using its installed shortcut; no task was retried.";
      }
      return this;
    }
    async request(path, options = {}) {
      if (!/^\/api\/runtime\/computer(?:\/|$)/.test(path) || path.includes("..")) throw new Error("Unsupported local operation");
      if (!this.authenticated || !this.csrf) throw new Error(this.reason);
      const method = options.method || "GET";
      const response = await this.fetch(path, {method, credentials: "same-origin", cache: "no-store", redirect: "error", signal: AbortSignal.timeout(10000), keepalive: options.keepalive === true,
        headers: {"Content-Type": "application/json", "X-Ghoti-CSRF": this.csrf},
        ...(options.body !== undefined ? {body: JSON.stringify(options.body)} : {})});
      const result = await response.json();
      if (!response.ok) {
        const error = new Error(typeof result.reason === "string" ? result.reason : "Local operation refused; not retried.");
        error.status = response.status;
        throw error;
      }
      return result;
    }
  }
  if (typeof module !== "undefined" && module.exports) module.exports = {LocalConnection};
  if (typeof window !== "undefined") {
    root.GhotiLocal = new LocalConnection();
    root.GhotiLocal.ready = root.GhotiLocal.bootstrap();
  }
})(typeof window !== "undefined" ? window : globalThis);

# Hermes Blocked Commands

        These commands stay blocked/manual later in N+6.2A.

        - `hermes setup` - provider/setup flow must be human-approved later
- `hermes login` - auth flow may request credentials or tokens
- `hermes auth` - auth/token flow is out of scope
- `hermes auth add` - token/provider configuration is out of scope
- `hermes provider` - provider setup is pending/not proven
- `hermes telegram` - Telegram is manual later/no token
- `hermes whatsapp` - live account messaging is out of scope
- `hermes browser` - browser/Playwright is degraded/not claimed
- `hermes computer-use` - click/type/control is future-gated
- `hermes gateway install` - external install/runtime wiring needs separate approval
- `hermes mcp install` - external install/runtime wiring needs separate approval

        Do not run provider setup, auth, Telegram setup, token commands, live
        APIs, browser automation, computer-use click/type, or account actions.

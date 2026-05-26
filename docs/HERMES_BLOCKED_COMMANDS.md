# Hermes Blocked Commands

These commands remain blocked or manual later in N+6.2A:

- `hermes setup`
- `hermes login`
- `hermes auth`
- `hermes auth add`
- `hermes provider`
- `hermes telegram`
- `hermes whatsapp`
- `hermes browser`
- `hermes computer-use`
- `hermes gateway install`
- `hermes mcp install`

Reason: they may configure providers, auth, tokens, Telegram, browser automation, computer-use control, external runtime wiring, or live APIs. No live API calls or live setup flows are run in this milestone.

Keep future provider, Telegram, and browser/computer-use work behind explicit human approval and a separate audit gate.

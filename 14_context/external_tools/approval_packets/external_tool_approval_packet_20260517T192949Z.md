# External Tool Runtime-Wiring Approval Packet — N+4.8A

Generated: 20260517T192949Z

This packet exists so a human can review each sandboxed external tool
BEFORE any real runtime wiring. Nothing in this packet wires, installs,
or runs anything. Approval is required per tool.

## Hard scope (current state)

- Repos cloned: sandbox static inspection only.
- Installs performed: NO.
- External repo code executed: NO.
- Desktop control enabled: NO.
- Live APIs / accounts connected: NO.
- Runtime wiring into Ghoti: NONE — adapter stubs only.

## Per-tool review

### UI-TARS Desktop (`bytedance/UI-TARS-desktop`)

- Purpose: Desktop GUI agent — screenshot capture and click/type control of the local computer.
- Clone status: cloned
- Commit: 7986f5aea500c4535c0e55dc5c5d0cda73767c45
- Ecosystems: node/javascript-typescript
- Install requirements (NOT installed): npm, pnpm
- API key / secret required: True
- Desktop-control risk: True
- Live-account risk: True
- License: Apache License

Human approval checklist before wiring UI-TARS Desktop:
- [ ] Static scan reviewed by a human
- [ ] Dependency install reviewed and explicitly approved
- [ ] Desktop-control / live-account risk explicitly accepted (if any)
- [ ] Sandbox-only execution boundary confirmed
- [ ] Operator signs off on runtime wiring

### UI-TARS Model (`bytedance/UI-TARS`)

- Purpose: UI-TARS vision-language GUI agent model and inference assets.
- Clone status: cloned
- Commit: 582f3a7ea5d285ee8ed9e2e84048d1ab01453c49
- Ecosystems: unknown
- Install requirements (NOT installed): none detected
- API key / secret required: True
- Desktop-control risk: True
- Live-account risk: False
- License: Apache License

Human approval checklist before wiring UI-TARS Model:
- [ ] Static scan reviewed by a human
- [ ] Dependency install reviewed and explicitly approved
- [ ] Desktop-control / live-account risk explicitly accepted (if any)
- [ ] Sandbox-only execution boundary confirmed
- [ ] Operator signs off on runtime wiring

### TheAgency (`the-agency-ai/the-agency`)

- Purpose: Multi-agent orchestration framework.
- Clone status: cloned
- Commit: dd2430bfe62c2e27c4e678b6879faffd1c2b372a
- Ecosystems: node/javascript-typescript
- Install requirements (NOT installed): npm
- API key / secret required: False
- Desktop-control risk: False
- Live-account risk: False
- License: MIT License

Human approval checklist before wiring TheAgency:
- [ ] Static scan reviewed by a human
- [ ] Dependency install reviewed and explicitly approved
- [ ] Desktop-control / live-account risk explicitly accepted (if any)
- [ ] Sandbox-only execution boundary confirmed
- [ ] Operator signs off on runtime wiring

### agent-skills-eval (`darkrishabh/agent-skills-eval`)

- Purpose: Agent skill benchmarking and evaluation harness.
- Clone status: cloned
- Commit: b60eebe3c6edaa917a284e13b9b0e9fa00f1c957
- Ecosystems: node/javascript-typescript
- Install requirements (NOT installed): npm
- API key / secret required: True
- Desktop-control risk: False
- Live-account risk: True
- License: MIT License

Human approval checklist before wiring agent-skills-eval:
- [ ] Static scan reviewed by a human
- [ ] Dependency install reviewed and explicitly approved
- [ ] Desktop-control / live-account risk explicitly accepted (if any)
- [ ] Sandbox-only execution boundary confirmed
- [ ] Operator signs off on runtime wiring

### Vouch Protocol (`vouch-protocol/vouch`)

- Purpose: Agent identity / attestation / vouching protocol.
- Clone status: cloned
- Commit: 1b37c3ef661bd1c4ed87c5349e51be7ce5038bcc
- Ecosystems: python
- Install requirements (NOT installed): pip
- API key / secret required: True
- Desktop-control risk: False
- Live-account risk: True
- License: Apache License 2.0

Human approval checklist before wiring Vouch Protocol:
- [ ] Static scan reviewed by a human
- [ ] Dependency install reviewed and explicitly approved
- [ ] Desktop-control / live-account risk explicitly accepted (if any)
- [ ] Sandbox-only execution boundary confirmed
- [ ] Operator signs off on runtime wiring

## Decision

- [ ] APPROVED for the next supervised wiring step
- [ ] NOT approved — remain sandbox/stub only

No tool is wired until a human checks the boxes above.

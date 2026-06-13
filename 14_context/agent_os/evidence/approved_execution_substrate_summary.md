# Approved Execution Substrate Summary

Ghoti now has one real supervised action path:

`worker suggestion -> Rust guard -> pending queue -> explicit approval -> Rust guard -> bounded repo-local artifact write -> run record + evidence + handoff`

What is enabled:

- Four allowlisted text/JSON artifact actions
- Three approved repo-local output roots
- Deterministic request fingerprints
- Approval state and ownership checks
- Inspectible queue state
- Command-center approval status and controls

What remains blocked:

- Commands and arbitrary process execution
- External/live writes
- Agents and swarms
- Browser/computer-use and mouse/keyboard input
- Accounts, email sending, Telegram actions, posting, purchases, and payments

Run the proof:

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --full-approved-demo --json
```

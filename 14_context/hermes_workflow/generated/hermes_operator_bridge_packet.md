# Hermes Operator Bridge Packet

Use this compact packet when planning the Hermes lane with ChatGPT,
Codex, or Claude.

- Status: Hermes workflow readiness: 58%. Hermes core is installed and skills are visible. Provider setup, Telegram, browser/Playwright, and Codex provider verification remain manual/unproven. Ghoti exposes status, skills index, manual setup plan, and future bridge packet with safe probes only and no live provider setup.
- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Context pack: `python 03_scripts/ghoti_product_launcher.py --context-pack --json`
- Repo Hermes bundle: `python 03_scripts/ghoti_product_launcher.py --repo-bundle hermes --json`
- Hermes bridge status: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Hermes bridge write: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`
- Skills visible: `78`
- Codex provider pending/not proven
- Telegram manual later/no token
- browser/Playwright degraded/not claimed
- No VPS

Safety: safe probes only; no live provider setup; no provider config;
no Telegram setup; no tokens; no browser automation; no live APIs.

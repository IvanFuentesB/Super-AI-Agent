# Simple Phone Game Pipeline

Date: 2026-04-28
Milestone: N+3.17
Status: planning_only / no_installs / no_app_store_actions

---

## Purpose

Document the future pipeline for building a simple hyper-casual phone game using AI-assisted Unity workflow. This is a planning artifact only. No Unity, Unity-MCP, app-store accounts, or monetization systems are installed or wired.

---

## Why Phone Games

- Low marginal cost per download at scale.
- Simple hyper-casual mechanics can be built by one developer.
- Google Play and App Store provide massive distribution with no upfront marketing spend (long-term).
- AI tools may dramatically reduce asset and code generation time.
- Rewarded ads and optional cosmetic IAP are well-understood monetization models for simple games.

---

## Idea Intake

| Field | Notes |
|---|---|
| Game title concept | _(e.g. "Tap Stack", "Color Sort", "Path Finder")_ |
| Core mechanic | _(one-sentence: "player taps to stack blocks without falling")_ |
| Genre | _(hyper-casual / puzzle / idle / runner)_ |
| Session length | _(target: 1–3 minutes per session)_ |
| Monetization model | _(rewarded ads / optional cosmetic IAP / none)_ |
| Target platforms | _(Android / iOS / both)_ |

---

## Core Mechanics Template

| Element | Description |
|---|---|
| Player input | _(tap / swipe / tilt / hold)_ |
| Win condition | _(reach level N / survive X seconds / achieve score)_ |
| Fail condition | _(fall off / time out / wrong tap)_ |
| Progression | _(speed increases / complexity increases / new elements unlock)_ |
| Restart loop | _(instant restart — critical for hyper-casual)_ |

---

## MVP Scope

Keep MVP scope minimal. Ship the simplest possible version that has a satisfying loop.

- [ ] One mechanic implemented and working
- [ ] 5–10 test levels
- [ ] Basic UI: score, restart button, level counter
- [ ] No advanced art — solid colors and basic shapes for MVP
- [ ] No login, no social features, no external API for MVP
- [ ] One interstitial ad slot (optional — only if approved)

---

## Monetization Options

| Model | Notes | Approval required |
|---|---|---|
| Rewarded ads (opt-in) | User watches ad for reward; low annoyance | Yes — ad network account |
| Interstitial ads (between levels) | Higher revenue, higher annoyance; use sparingly | Yes — ad network account |
| Cosmetic IAP (skins only) | Low risk, no pay-to-win | Yes — IAP account setup |
| Remove-ads IAP | Simple one-time purchase | Yes — IAP account setup |
| Subscription | Not recommended for hyper-casual | N/A |

**No real-money trading, loot boxes, or gambling mechanics.**

---

## Asset Pipeline

| Asset type | AI-assisted path | Notes |
|---|---|---|
| Icons and UI sprites | Midjourney / DALL-E / Stable Diffusion | Verify IP/license before use |
| Background music | Royalty-free (e.g. Pixabay, Freepd) | Check license for commercial use |
| Sound effects | Royalty-free or Audacity-generated | |
| Store art (icon + screenshots) | AI-generated or designed | Needs human review |

---

## Unity Workflow

All Unity work requires operator approval and a separate install decision.

- **Candidate tool:** `ivanmurzak/Unity-MCP` — tracked as a future AI-assisted Unity workflow candidate
- **Status:** NOT installed, NOT wired, planning_only
- **Approval required before:** any Unity install, plugin wiring, editor scripting, or build

General Unity path:
1. Install Unity via Unity Hub (free Personal license for solo indie dev)
2. Create new 2D project
3. Implement mechanic in C#
4. Test on Android emulator or connected device
5. Build signed APK
6. Submit to Google Play via Play Console

---

## Google Play / App Store Path

| Step | Notes | Approval required |
|---|---|---|
| Create developer account | $25 one-time for Google Play; $99/year for Apple | Yes — payment |
| Build signed APK/IPA | Local build step | No |
| Upload to Play Console / App Store Connect | Account required | Yes |
| Store listing (title, description, screenshots) | Operator reviews before publish | Yes |
| Pricing and in-app products | IAP setup requires account | Yes |
| App review submission | Triggers Apple/Google review | Yes |

**No app-store account actions without explicit operator approval.**

---

## Analytics Plan

| Tool | Purpose | Notes |
|---|---|---|
| Unity Analytics (built-in) | Session length, retention, funnel | Free, GDPR review needed |
| Firebase (optional) | Events, crash reporting, A/B | Free tier available |
| Manual spreadsheet | Simple tracking for MVP | No account needed |

No behavioral tracking, no third-party ad tracking, no analytics beyond what is disclosed in the store listing privacy policy.

---

## Risk Checks

- [ ] No IAP or ad network wiring without approval
- [ ] No app-store account creation without approval
- [ ] No payment setup without approval
- [ ] No loot boxes, gambling mechanics, or predatory IAP
- [ ] Age rating reviewed (PEGI / ESRB / IARC)
- [ ] Privacy policy required before store submission
- [ ] Unity license review (Personal tier restrictions)
- [ ] AI-generated asset IP and license verified before commercial use
- [ ] No Unity-MCP install without explicit approval

---

## Candidate Tool

`ivanmurzak/Unity-MCP` — tracked as a future AI-assisted Unity Game Developer workflow tool.
- Do NOT install, clone, or wire without explicit operator approval.
- Evaluation: review GitHub README, license, and sandbox plan first.

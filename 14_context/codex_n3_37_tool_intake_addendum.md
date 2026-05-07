# Codex N+3.37 Tool Intake Addendum

Status: codex_audit_only / tool_research_addendum / no_installs / no_connections

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack

## Source Check Notes

Web/network source checks were available. This addendum uses public source checks only and does not install, clone, run, connect, or authenticate any tool.

Important safety stance:

- research now
- connect later only with explicit approval
- default to local/read-only/draft-only
- never connect OSINT, account, payment, posting, or live creative tools into autonomous execution

## Source URLs Consulted

- Claude Code MCP docs: https://docs.claude.com/en/docs/claude-code/mcp
- Claude Code permission/plan mode docs: https://code.claude.com/docs/en/permission-modes
- Claude Code ultrareview docs: https://code.claude.com/docs/en/ultrareview
- Claude creative connector reporting: https://www.techradar.com/pro/claude-cant-replace-taste-or-imagination-but-it-can-open-up-new-ways-of-working-anthropic-signs-up-adobe-blender-and-more-to-push-claude-into-creative-work
- Claude connector reporting: https://www.macrumors.com/2026/04/28/claude-creative-tool-connectors/
- SketchVLM project: https://sketchvlm.github.io/
- Bulwark: https://www.getbulwark.ai/
- Paseo docs: https://paseo.sh/docs/skills
- Paseo GitHub: https://github.com/getpaseo/paseo
- Prompt Master GitHub: https://github.com/nidhinjs/prompt-master
- Honcho docs: https://docs.honcho.dev/
- Skene: https://www.skene.ai/
- SpiderFoot: https://spiderfoot.org/
- Hudson Rock API docs: https://docs.hudsonrock.com/reference/search-by-domains
- Intelligence X limits: https://help.intelx.io/api/limits/
- WiGLE API: https://api.wigle.net/
- Higgsfield: https://higgsfield.ai/
- Higgsfield OpenAI customer story: https://openai.com/index/higgsfield/
- Arcads: https://www.arcads.co/
- Kling reporting/source pages: https://ir.kuaishou.com/node/11216/pdf
- Seedance official: https://seed.bytedance.com/en/seedance
- Picsart image-to-video: https://picsart.com/image-to-video
- European Commission GDPR lawful basis/legitimate interest pages: https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/legal-grounds-processing-data_en

## Tool / Concept Intake Table

| Tool or concept | What it might be useful for | Safe use case | Risk | Approval gate | Priority | Connect now? |
|---|---|---|---|---|---|---|
| Claude Code MCP bridge | Let Claude Code read local Ghoti state through MCP | Project-scoped stdio server exposing read-only status tools | MCP servers can widen tool authority if misconfigured | Require source audit, exact `claude mcp get`, read-only tool list | now | No, verify existing bridge first |
| Local Gemma/Ollama worker through Ghoti/MCP | Let Claude ask Ghoti for local draft summaries without using Claude as the model | Read-only status plus explicit artifact paths; later a draft-only request queue | If exposed as a write/run tool, Claude could trigger local model runs unexpectedly | Separate approval for any model-run tool; artifact-only; no execution | soon | Research only |
| Claude creative connectors: Fusion 360, Blender, Adobe, Claude Design | Creative/engineering workflows, asset drafts, 3D/CAD review, video/image editing | Human-driven creative assist with local/exported assets | Live app control, paid accounts, IP/copyright, accidental publishing/export | Per-app approval, account approval, asset/IP review | later | No |
| SketchVLM | Visual pointing/annotation and explanation workflows | Research pattern for screenshots/diagrams; possible local annotation spec | Visual model hallucination, wrong annotations, accessibility issues | Human review before using annotations as truth | later | Research only |
| Bulwark | AI agent governance, audit, permission control concepts | Extract patterns: policy checks, audit logs, approval enforcement | Installing governance layer changes execution trust boundary | Explicit install/eval approval | later | Research only |
| Paseo | Agent orchestration across Claude/Codex/other coding agents | Isolated evaluation of worker orchestration patterns | Multi-agent edits can collide or corrupt working tree | Explicit install/eval approval; worktree isolation | later | Research only |
| nidhinjs/prompt-master | Token-saving prompt generation skill | Read-only prompt quality research; maybe adapt prompt patterns into local docs | Installing skills into `.claude/skills` can alter Claude behavior | Explicit skill install approval | soon | Research only |
| Honcho | Agent memory research and cross-session memory patterns | Compare with Ghoti compact memory and Obsidian local memory | Hosted memory may store sensitive data externally | No secrets; explicit data boundary review | later | Research only |
| Skene | Product/growth/onboarding analysis from repo context | Use as inspiration for Money OS growth/onboarding review docs | Repo/account/Supabase access and automated growth actions | Explicit approval for any account/API use | later | Research only |
| `/ultrareview` | Claude Code multi-agent code review workflow | Use after implementation milestones for independent review | Can consume credits and may expose code to cloud review | Operator approval before use | soon | Not from Codex |
| `/plan` mode | Read-only planning before edits | Require plan-first for risky/multi-file Claude milestones | False sense of safety if plan is approved too broadly | Human approves plan before implementation | now | Workflow pattern only |
| npxskillui | Possible UI/skill workflow research | Source audit only; maybe inspect generated skills later | npx install/run supply-chain risk | Explicit install/run approval | later | Research only |
| Hudson Rock | Cybercrime intelligence / compromised credential exposure checks | Defensive check of operator-owned domains only | Sensitive breach data, paid API, privacy/legal risk | Explicit owner approval and legal scope | later | No |
| Metagoofil | Metadata extraction from public documents | Defensive metadata audit of owned documents/domains only | Can become recon/scraping; search engine blocking; privacy risk | Explicit target ownership and scope | later | No |
| SpiderFoot | OSINT automation framework | Defensive OSINT on owned assets only | Active/passive recon risk, legal/TOS issues, noisy collection | Written target authorization | later | No |
| IntelX | Search/leaks intelligence | Defensive check of owned emails/domains only | Sensitive data, API limits, privacy risk | Explicit target ownership and legal review | later | No |
| WiGLE | Wireless network lookup API | Defensive audit of operator-owned network exposure only | Location/privacy sensitivity | Explicit owner approval | later | No |
| Picsart-like flows | Fast content editing, resizing, clipping | Manual asset editing drafts only | Copyright, account actions, paid credits, publishing | Human asset/IP/account approval | soon | No |
| Higgsfield | AI video/image generation and social video workflows | Draft storyboards/prompts and manual generation checklist | Paid credits, content rights, likeness/deepfake risk | Human approval before generation/public use | soon | No |
| Arcads | AI ad/video generation | Draft ad concepts and scripts | Ad claims, paid credits, platform policies | Human review and proof check | later | No |
| Kling | AI video generation/editing | Draft-only prompt plan; manual generation after rights review | Copyright/IP/likeness risk; paid credits | Human approval and IP review | later | No |
| Seedance | AI video generation | Research-only until licensing/platform status is clear | High IP/copyright sensitivity and regional/platform uncertainty | Explicit legal/IP review | later | No |
| Internship outreach volume workflow | Find companies, rank fit, draft applications | Official application route first; personalized drafts only | GDPR, spam, private email harvesting, reputational risk | Human approval before every send | now | No live sending |
| YouTube/TikTok/Instagram faceless channel management | Content experiments and distribution | Local script/asset/calendar drafts; manual posting only | Account bans, fake engagement, child-safety, IP claims | Human approval before account/post/action | soon | No |

## Near-Term Priority

Now:

- keep N+3.18 pushed and stable
- verify Ghoti MCP connection from Claude side
- keep MCP read-only
- use `/plan` and docs-first workflows for risky changes
- use prompt-master-style ideas only as research, not installed skill behavior

Soon:

- content workflow specs for faceless channels
- internship outreach tracking and drafting workflow
- local Gemma-assisted draft generation
- manual review queues

Later:

- creative connectors
- Paperclip/OpenClaw/n8n/Paseo/Bulwark
- Honcho/Skene research
- OSINT tools under strict owner-approved defensive scope

Reject for now:

- autonomous posting/selling/outreach/payment
- broad OSINT automation
- any connector with live account mutation
- child-targeted content automation without extra compliance review

## Tooling Verdict

Do not connect more tools now.

First verify the read-only Ghoti MCP bridge in Claude Code and proceed with the Money OS sequence. Treat all new tools as research-only until an explicit approval-gated evaluation milestone exists.

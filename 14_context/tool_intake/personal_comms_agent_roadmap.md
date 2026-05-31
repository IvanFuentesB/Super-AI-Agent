# Personal Communications Agent Roadmap (candidate-only)

Status: **candidate_only**, planning only. These are the personal-communications
ideas extracted from Odysseus, recorded as gated modules. Nothing is installed,
wired, or logged into. The hard rule for all of them: **draft-only first, the human
sends.**

## Cross-cutting rules (apply to every module here)

- **Draft-only first.** The agent produces labeled DRAFTs; it never sends.
- **No auto-send.** No message or email is sent automatically. Outbound always needs
  explicit human approval.
- **No destructive mailbox/chat actions.** No deleting, archiving, or moving messages
  until a separate, approved milestone allows it.
- **No mass replies, no spam, no fake engagement.**
- **No account login** (email, WhatsApp, calendar) until a separate, approved
  milestone using each provider's official API.
- **Credentials are never stored** in the repo or the Obsidian vault. Any future
  real-account access supplies credentials at run time only.
- **Local fixtures first.** Early work runs on exported sample data, not live accounts.

## Email Triage + Reply Drafts

- **Value:** summaries, urgency scoring, tags, labeled reply DRAFTs, and spam flagging
  to save time.
- **Local-first path:** run over a local fixture mailbox with a local model; output
  summaries, tags, urgency, and labeled DRAFT replies as files.
- **External path (gated):** real mailbox via the provider's official API, read-only
  first, a separate approved milestone; credentials are never stored.
- **First safe test:** triage a local fixture of sample emails; produce a labeled
  DRAFT reply; nothing is sent, deleted, archived, or moved.
- **Forbidden now:** sending, auto-reply, delete/archive/move, account login,
  credential storage, mass/bulk replies, spam.

## WhatsApp Summary + Reply Drafts

- **Value:** summarize chats and prepare labeled reply DRAFTs.
- **Local-first path:** run over a local fixture chat export with a local model;
  output summaries and labeled DRAFT replies.
- **External path (gated, blocked-adjacent):** real WhatsApp access needs its own
  approved milestone; no login now; credentials are never stored.
- **First safe test:** summarize a fixture chat export and produce a labeled DRAFT
  reply; nothing is sent; no login.
- **Forbidden now:** sending, auto-reply, account login, credential storage, mass/bulk
  replies, fake engagement.

## Calendar / Tasks / Reminders Agent

- **Value:** surface events and manage tasks/reminders as drafts the user confirms.
- **Local-first path:** local task/reminder files; propose additions; the user
  confirms; no live-calendar write.
- **External path (gated):** calendar sync via an official API, read-only first, a
  separate approved milestone; credentials are never stored.
- **First safe test:** propose a draft event/reminder into a local file; never write a
  real calendar automatically.
- **Forbidden now:** writing to a live calendar, account login, credential storage.

## Personal Style Memory - "thinks like me", approval-gated

The agent may draft in the user's voice, but never *be* the user without approval.

- **Explicit preference memory.** Style is captured in an explicit, user-curated
  memory file - not inferred secretly.
- **Editable and deletable.** The user can read, edit, and delete the memory at any
  time.
- **Label drafts as DRAFT.** Anything written in the user's style is labeled DRAFT.
- **Human approves outbound.** No message goes out without explicit human approval.
- **No impersonation without approval.** The agent never claims to be the user, or
  acts as them, without approval.
- **No sensitive profiling** unless the user explicitly approves it.

## AI Video Self-Editing Pipeline

- **Value:** assist editing the user's own videos (cuts, captions, drafts).
- **Local-first path:** a local pipeline over user-approved assets only; produce export
  drafts for manual upload.
- **External path (gated):** any cloud render/upload is a separate approved milestone;
  there is no automated posting.
- **First safe test:** run a local edit over an approved sample asset and export a
  draft; no posting.
- **Forbidden now:** scraping copyrighted material, automated posting, fake engagement.

## Not enabled by this roadmap

No email login, no WhatsApp login, no Telegram setup, no MCP, no browser-use, no
computer-use. No auto-send, no social posting, no live account action. Credentials
are never stored. `main` is untouched.

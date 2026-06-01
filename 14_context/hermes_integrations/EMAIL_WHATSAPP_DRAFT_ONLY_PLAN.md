# Email / WhatsApp Draft-Only Plan (Phase 6, planned_only)

Status: **planned_only**. Email and WhatsApp are **not enabled**. There is **no account
login** and **no auto-send**. This is a draft-only design for a future, approval-gated
milestone.

## Hard rules (draft-only)

- **Draft-only first.** The agent prepares labeled DRAFTs; the human sends.
- **No auto-send.** There is no auto-send; no email or message is sent automatically.
- **No account login.** No email login and no WhatsApp login by this milestone.
- **No credentials in the repo.** No login credentials are stored in the repo, in
  Obsidian, or in prompts.
- **No mass replies.** No bulk or mass replies, no spam, no fake engagement.
- **No destructive mailbox/chat actions.** No deleting, archiving, or moving messages
  without explicit human approval.
- **Local fixtures first.** Early work runs on exported sample data, not live accounts.

## Flags

`email_whatsapp_enabled: false`. `auto_send: false`. `account_login: false`.
`credentials_stored: false`. `requires_human_approval: true`.

## Not enabled now

No email/WhatsApp login, no auto-send, no live account action. Any future real-account
access is a separate, approved milestone using an official API, with credentials supplied
at run time only and never stored.

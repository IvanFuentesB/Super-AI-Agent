# Hermes Telegram Manual Setup Plan

Telegram integration is intentionally manual and later.

## Human-Owned Steps

1. Create a Telegram bot manually through Telegram.
2. Record the bot token in a local `.env` file only.
3. Record the intended chat ID locally only.
4. Run a local validation command after Ghoti adds an explicit audited Telegram
   setup milestone.

## Repository Rules

- No Telegram bot token is committed.
- No chat ID is committed.
- `.env.example` contains placeholders only.
- No Telegram message is sent in this milestone.
- No live account action is performed without human approval.

## Placeholder Names

```text
HERMES_TELEGRAM_BOT_TOKEN=
HERMES_TELEGRAM_CHAT_ID=
```

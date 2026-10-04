# Telegram bot starter for Railway (Python)

A minimal Telegram bot on the official Bot API with `python-telegram-bot` 22: long polling, so no
domain or webhook to set up, and a log that says what is wrong when the token is.

## Setup

1. In Telegram, open [@BotFather](https://t.me/BotFather), send `/newbot` and copy the token.
2. Deploy the template and paste the token into `TELEGRAM_BOT_TOKEN`.
3. The log prints `Logged in as @yourbot`. Open the bot and send `/start`.

## Why this exists

The common Python Telegram starter on Railway hides a wrong token. When the token is missing or
rejected, it prints an error and then sleeps forever so that the service does not restart in a
loop. But Python buffers standard output when it is not a terminal, so that error never reaches
the log: the deploy shows green, the log shows only `Starting Container`, and the bot never
answers.

Here:

- **Output is unbuffered** (`PYTHONUNBUFFERED=1`), so every log line appears as it happens.
- **The token is checked before polling starts.** A missing token and a token Telegram rejects
  each get one plain sentence saying where to fix it, and the process exits with an error, so the
  deploy shows as crashed instead of green. The rejected token is not echoed into the log.
- **A second copy of the bot is named, not hidden.** Telegram lets only one process poll a token;
  if another one is running, the log says so instead of repeating an error.
- **The start command is in the Dockerfile**, not in `railway.json`, which Railway no longer reads
  for services created from a template.

## Commands

- `/start` - greeting
- `/help` - list of commands
- any text - echoed back

Add handlers in `main.py`; see the [python-telegram-bot docs](https://docs.python-telegram-bot.org).

## Run locally

```bash
docker build -t telegram-bot .
docker run --rm -e TELEGRAM_BOT_TOKEN=123:abc telegram-bot
```

## License

MIT

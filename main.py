"""A minimal Telegram bot on the official Bot API, using long polling.

It needs only a token from @BotFather in TELEGRAM_BOT_TOKEN. Long polling keeps the bot
working without a public domain or a webhook.
"""

import asyncio
import logging
import os
import sys

from telegram import Bot, BotCommand, Update
from telegram.error import Conflict, InvalidToken
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# httpx logs every getUpdates request at INFO, which buries the bot's own lines
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN:
    log.error(
        "TELEGRAM_BOT_TOKEN is not set. Create a bot with @BotFather in Telegram, "
        "then add the token as a service variable in Railway."
    )
    sys.exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm running on Railway. Send me any text and I'll echo it.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/start - say hello\n/help - this message\nAny text - echoed back")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, Conflict):
        # Telegram allows one getUpdates consumer per bot. During a redeploy the old and the new
        # container overlap for a moment; anything longer means a second copy is running.
        log.warning(
            "Another process is polling with this token. If this lasts past a redeploy, stop the "
            "other copy of the bot (or remove its webhook) - only one can receive updates."
        )
        return
    log.error("Unhandled error while processing an update", exc_info=context.error)


async def check_token() -> None:
    # Checked before polling starts: once the application runs, the library reports a rejected
    # token with a traceback that prints the token itself.
    try:
        async with Bot(TOKEN) as bot:
            await bot.get_me()
    except InvalidToken:
        log.error(
            "Telegram rejected the token. Copy it again from @BotFather (/mybots -> your bot -> "
            "API Token) and update TELEGRAM_BOT_TOKEN."
        )
        sys.exit(1)


async def post_init(app: Application) -> None:
    me = await app.bot.get_me()
    await app.bot.set_my_commands([BotCommand("start", "Say hello"), BotCommand("help", "Show commands")])
    log.info("Logged in as @%s (id %s). Open https://t.me/%s and send /start", me.username, me.id, me.username)


def main() -> None:
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(on_error)
    # A webhook left over from another deployment would make getUpdates fail; drop it.
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(check_token())
    main()

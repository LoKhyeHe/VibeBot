"""Telegram bot for PatchUp welcome messaging."""

from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = (
    "👋 Welcome to PatchUp!\n\n"
    "PatchUp is your one-stop 3D printing service platform — from idea to finished print.\n"
    "Need prototypes, custom parts, or creative models? We make 3D printing simple, fast, and reliable."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send PatchUp welcome message when the /start command is issued."""
    if update.message is None:
        return

    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display available commands."""
    if update.message is None:
        return

    await update.message.reply_text("Use /start to get the PatchUp welcome message.")


def main() -> None:
    """Run the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing TELEGRAM_BOT_TOKEN environment variable. "
            "Set it before starting the bot."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("PatchUp Telegram bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

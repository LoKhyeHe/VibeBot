"""Telegram bot for PatchUp lead-to-order workflow."""
"""Telegram bot for PatchUp welcome messaging."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

(
    MAIN_MENU,
    STRUCTURED_REQUEST,
    QUOTE_DECISION,
    DEPOSIT_PROOF,
    BALANCE_PAYMENT,
    DELIVERY,
    FEEDBACK,
) = range(7)

MENU_KEYBOARD = ReplyKeyboardMarkup(
    [["🛠️ Start Order"], ["📦 View Order"], ["💬 Submit Feedback"]],
    resize_keyboard=True,
)


def _set_stage(context: ContextTypes.DEFAULT_TYPE, stage: str) -> None:
    context.user_data["stage"] = stage


def _get_stage(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("stage", "Lead received")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point when user opens bot."""
    if update.message is None:
        return MAIN_MENU

    _set_stage(context, "Lead received")
    await update.message.reply_text(
        "👋 *Welcome to PatchUp*\n"
        "Your one-stop 3D printing service platform.\n\n"
        "Here is how your order flows:\n"
        "1) Lead received\n"
        "2) Structured request\n"
        "3) Review + slicing\n"
        "4) Quote sent (24h expiry)\n"
        "5) Quote accepted\n"
        "6) Deposit requested + proof\n"
        "7) Deposit confirmed\n"
        "8) Printing\n"
        "9) Completion notice\n"
        "10) Balance payment\n"
        "11) Delivery/meetup\n"
        "12) Feedback request\n\n"
        "Choose an option below to continue 👇",
        parse_mode="Markdown",
        reply_markup=MENU_KEYBOARD,
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle top-level choices."""
    if update.message is None:
        return MAIN_MENU

    choice = update.message.text.strip()

    if choice == "🛠️ Start Order":
        _set_stage(context, "Structured request")
        await update.message.reply_text(
            "Great — let's start your order.\n\n"
            "Please send your request in this format:\n"
            "Name: <your name>\n"
            "Part: <what to print>\n"
            "Material: <PLA/PETG/ABS/Resin>\n"
            "Quantity: <number>\n"
            "Deadline: <date/time>\n"
            "Notes: <color, finish, tolerance, etc.>\n\n"
            "You can paste all fields in one message.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return STRUCTURED_REQUEST

    if choice == "📦 View Order":
        await update.message.reply_text(
            f"Current order stage: *{_get_stage(context)}*", parse_mode="Markdown"
        )
        await update.message.reply_text("Choose your next action.", reply_markup=MENU_KEYBOARD)
        return MAIN_MENU

    if choice == "💬 Submit Feedback":
        await update.message.reply_text(
            "Please share your feedback. We read every message 🙌",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FEEDBACK

    await update.message.reply_text("Please choose one of the menu buttons.", reply_markup=MENU_KEYBOARD)
    return MAIN_MENU


async def receive_structured_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive request, then move into review and quoting."""
    if update.message is None:
        return STRUCTURED_REQUEST

    context.user_data["request"] = update.message.text.strip()
    _set_stage(context, "Review + slicing")

    await update.message.reply_text(
        "✅ Request received.\n"
        "Our team is now reviewing your file(s) and preparing slicing settings."
    )

    expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    context.user_data["quote_expiry"] = expiry.strftime("%Y-%m-%d %H:%M UTC")
    _set_stage(context, "Quote sent (24h expiry)")

    await update.message.reply_text(
        "💸 *Quote Ready*\n"
        "Estimated total: *$120*\n"
        "Required deposit: *$60*\n"
        f"Quote expires: *{context.user_data['quote_expiry']}*\n\n"
        "Reply with: `ACCEPT` to continue or `DECLINE` to stop.",
        parse_mode="Markdown",
    )
    return QUOTE_DECISION


async def handle_quote_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return QUOTE_DECISION

    decision = update.message.text.strip().upper()

    if decision == "ACCEPT":
        _set_stage(context, "Deposit requested + proof")
        await update.message.reply_text(
            "🎉 Quote accepted.\n"
            "Please pay the *$60 deposit* and reply with payment proof/reference.",
            parse_mode="Markdown",
        )
        return DEPOSIT_PROOF

    if decision == "DECLINE":
        _set_stage(context, "Lead received")
        await update.message.reply_text(
            "No problem. Your quote is closed. You can start again anytime.",
            reply_markup=MENU_KEYBOARD,
        )
        return MAIN_MENU

    await update.message.reply_text("Please reply with `ACCEPT` or `DECLINE`.")
    return QUOTE_DECISION


async def handle_deposit_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return DEPOSIT_PROOF

    context.user_data["deposit_proof"] = update.message.text.strip()
    _set_stage(context, "Deposit confirmed")
    await update.message.reply_text("✅ Deposit confirmed.")

    _set_stage(context, "Printing")
    await update.message.reply_text("🖨️ Printing has started. We'll notify you once complete.")

    _set_stage(context, "Completion notice")
    await update.message.reply_text(
        "📣 Printing complete. Please pay the *remaining balance of $60* and send proof.",
        parse_mode="Markdown",
    )
    return BALANCE_PAYMENT


async def handle_balance_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return BALANCE_PAYMENT

    context.user_data["balance_proof"] = update.message.text.strip()
    _set_stage(context, "Balance payment")
    await update.message.reply_text("✅ Balance payment received.")

    _set_stage(context, "Delivery/meetup")
    await update.message.reply_text(
        "Choose delivery method:\n- Reply `DELIVERY` for courier\n- Reply `MEETUP` for collection"
    )
    return DELIVERY


async def handle_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return DELIVERY

    method = update.message.text.strip().upper()
    if method not in {"DELIVERY", "MEETUP"}:
        await update.message.reply_text("Please reply with `DELIVERY` or `MEETUP`.")
        return DELIVERY

    context.user_data["delivery_method"] = method
    await update.message.reply_text(f"🚚 {method.title()} confirmed.")

    _set_stage(context, "Feedback request")
    await update.message.reply_text(
        "🙏 Thanks for ordering with PatchUp! Please share your feedback.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FEEDBACK


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return FEEDBACK

    context.user_data["feedback"] = update.message.text.strip()
    _set_stage(context, "Closed")
    await update.message.reply_text(
        "Thank you! Your feedback has been recorded.\n"
        "If you'd like another print, tap Start Order below.",
        reply_markup=MENU_KEYBOARD,
    )
    return MAIN_MENU


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "Use /start to open the menu.\n"
        "Flow supported: lead → structured request → quote → deposit → printing → completion → balance → delivery/meetup → feedback."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        await update.message.reply_text("Cancelled. Use /start to begin again.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            STRUCTURED_REQUEST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_structured_request)
            ],
            QUOTE_DECISION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quote_decision)
            ],
            DEPOSIT_PROOF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit_proof)
            ],
            BALANCE_PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_balance_payment)
            ],
            DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delivery)],
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("PatchUp Telegram bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

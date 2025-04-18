import logging
import os
import nest_asyncio
nest_asyncio.apply()

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to track user invites
user_invites = {}
pending_joins = {}
REQUIRED_INVITES = 10

# Welcome new users and assign inviter if they joined via link
async def track_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.new_chat_members is None:
        return
    for member in update.message.new_chat_members:
        user_id = member.id
        if user_id in pending_joins:
            inviter_id = pending_joins[user_id]
            user_invites.setdefault(inviter_id, set()).add(user_id)
            del pending_joins[user_id]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Welcome {member.full_name}!"
        )

# Track users attempting to post
async def track_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    invited = user_invites.get(user_id, set())

    if len(invited) < REQUIRED_INVITES:
        try:
            await update.message.delete()
        except Exception as e:
            logger.warning(f"Failed to delete message: {e}")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"You need to invite at least {REQUIRED_INVITES} friends to post.\n"
                f"You have invited {len(invited)}."
            )
        )

# Handle deep links from private messages
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    args = context.args
    if args:
        try:
            inviter_id = int(args[0])
            pending_joins[update.effective_user.id] = inviter_id
        except ValueError:
            logger.warning("Invalid inviter ID format in deep link.")

    await update.message.reply_text(
        "Thanks for starting the bot! If you joined a group, your inviter gets credit."
    )

# Run bot application
async def run_bot():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_joins))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_posts))
    app.add_handler(CommandHandler("start", start))

    logger.info("Bot started.")
    await app.run_polling()  # this handles init, start, polling, and idle

# Compatibility for environments with running loops
if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except RuntimeError as e:
        if "already running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(run_bot())
            loop.run_forever()
        else:
            raise

            raise





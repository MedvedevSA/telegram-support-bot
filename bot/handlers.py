from datetime import timedelta

from telegram import Update, Message
from telegram.ext import ContextTypes

from bot import schemas
from bot.utils import logging
from bot.settings import (
    TELEGRAM_SUPPORT_CHAT_ID,
    FORWARD_MODE,
    PERSONAL_ACCOUNT_CHAT_ID,
    WELCOME_MESSAGE,
)

logger = logging.get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        f"{WELCOME_MESSAGE} {update.effective_user.first_name}"
    )

def get_bot_data(context: ContextTypes.DEFAULT_TYPE) -> schemas.BotData:
    if not context.bot_data:
        context.bot_data.update({
            'recent_user_activity': {},
        })
    return schemas.BotData.model_validate(context.bot_data)
        
def bot_data_update(context: ContextTypes.DEFAULT_TYPE, bot_data: schemas.BotData):
    context.bot_data.update(bot_data.model_dump(mode='json'))

async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data = get_bot_data(context)
    async def process_forwarded_message(message: Message):

        send_default_reply = True
        for user_id, message_date in bot_data.recent_user_activity.items():
            if (
                user_id == update.effective_user.id and
                message.date - timedelta(hours=1) < message_date
            ):
                send_default_reply = False

        if send_default_reply:
            await update.message.reply_text("Ответим вам ближайшее время 😊")

        bot_data.recent_user_activity[update.effective_user.id] = update.message.date

        bot_data_update(context, bot_data)
        logger.info(
            f"Forwarded message ID: {forwarded_msg.message_id} from user ID: {update.effective_user.id}"
        )

        
    """Forward user messages to the support group or personal account."""
    if FORWARD_MODE == "support_chat":
        forwarded_msg = await update.message.forward(TELEGRAM_SUPPORT_CHAT_ID)
    elif FORWARD_MODE == "personal_account":
        forwarded_msg = await update.message.forward(PERSONAL_ACCOUNT_CHAT_ID)
    else:
        await update.message.reply_text("Invalid forwarding mode.")
        return

    if forwarded_msg:
        await process_forwarded_message(forwarded_msg)
    else:
        await update.message.reply_text(
            "Sorry, there was an error forwarding your message. Please try again later."
        )


async def forward_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward messages from the group or personal account back to the user."""
    logger.info("forward_to_user called")
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        logger.info("Message is a reply to another message")

        forward_from = update.message.reply_to_message.api_kwargs.get('forward_from') or {}
        user_id = forward_from.get('id')
        if user_id:
            logger.info(f"answear to, User ID: {user_id}")
            try:
                await context.bot.send_message(
                    chat_id=user_id, text=update.message.text
                )

            except Exception as e:
                logger.error(f"Error sending message to user: {str(e)}")
                await update.message.reply_text(
                    f"Error sending message to user: {str(e)}"
                )
        else:
            logger.warning("Could not find the user to reply to.")
            await update.message.reply_text("Could not find the user to reply to.")
    else:
        logger.warning("This message is not a reply to a forwarded message.")
        await update.message.reply_text(
            "This message is not a reply to a forwarded message."
        )

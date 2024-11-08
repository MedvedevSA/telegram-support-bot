import asyncio

import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.utils import logging
from bot.handlers import start, forward_to_group, forward_to_user
from bot.settings import TELEGRAM_TOKEN, TELEGRAM_SUPPORT_CHAT_ID, PERSONAL_ACCOUNT_CHAT_ID

logging.file_config('./logging_config.json')

logger = logging.get_logger(__name__)

# Create an event to signal when to stop the bot
stop_event = asyncio.Event()


async def main():
    # Initialize bot and application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND
            & ~filters.Chat(
                chat_id=[
                    TELEGRAM_SUPPORT_CHAT_ID,
                    # PERSONAL_ACCOUNT_CHAT_ID,
                ]
            ),
            forward_to_group,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Chat(chat_id=[TELEGRAM_SUPPORT_CHAT_ID, PERSONAL_ACCOUNT_CHAT_ID])
            & filters.REPLY,
            forward_to_user,
        )
    )

    logger.info("Handlers registered.")

    # Set up signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(application)))

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot started. Press Ctrl+C to stop.")

    # Wait until the stop event is set
    await stop_event.wait()

    # Stop the bot gracefully
    await application.stop()
    await application.shutdown()


async def shutdown(application: Application):
    """Gracefully shut down the application."""
    logger.info("Received stop signal, shutting down...")
    stop_event.set()


if __name__ == "__main__":
    asyncio.run(main())

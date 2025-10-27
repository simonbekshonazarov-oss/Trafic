"""
Telegram bot for Traffic Share
"""

import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from traffic_share.server.config import settings
from traffic_share.server.logger import logger
from traffic_share.bot.handlers.user_handlers import (
    start_command, help_command, balance_command, stats_command
)
from traffic_share.bot.handlers.admin_handlers import (
    admin_panel_command, users_command, system_command
)
from traffic_share.bot.handlers.callback_handlers import button_callback


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def create_bot_application():
    """Create and configure bot application"""
    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # User handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Admin handlers
    application.add_handler(CommandHandler("admin", admin_panel_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("system", system_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Telegram bot application created")
    
    return application


async def send_login_code(telegram_id: int, code: str):
    """Send login code to user"""
    try:
        application = create_bot_application()
        await application.bot.send_message(
            chat_id=telegram_id,
            text=f"🔐 Your login code: `{code}`\n\nUse this code to login to the app.",
            parse_mode="Markdown"
        )
        logger.info(f"Login code sent to {telegram_id}")
    except Exception as e:
        logger.error(f"Failed to send login code: {e}")


async def send_notification(telegram_id: int, message: str, title: str = None):
    """Send notification to user"""
    try:
        application = create_bot_application()
        
        text = f"📢 *{title}*\n\n{message}" if title else message
        
        await application.bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown"
        )
        logger.info(f"Notification sent to {telegram_id}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


async def notify_admin(message: str):
    """Notify admin channel"""
    try:
        admin_ids = settings.get_admin_ids()
        if not admin_ids:
            return
        
        application = create_bot_application()
        
        for admin_id in admin_ids:
            await application.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 *Admin Alert*\n\n{message}",
                parse_mode="Markdown"
            )
        
        logger.info("Admin notification sent")
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")


def run_bot():
    """Run the bot"""
    logger.info("Starting Telegram bot...")
    
    application = create_bot_application()
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()

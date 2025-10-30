"""
User command handlers for Telegram bot
"""

from telegram import Update
from telegram.ext import ContextTypes

from traffic_share.server.database import get_db_context
from traffic_share.server.models import User
from traffic_share.server.logger import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    welcome_message = """
👋 Welcome to Traffic Share!

You can earn money by sharing your internet traffic through our app.

📱 Download the app and login with your Telegram account.

Use /help to see available commands.
    """
    
    await update.message.reply_text(welcome_message)
    
    logger.info(f"User {telegram_id} ({username}) started bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *Available Commands:*

/start - Start the bot
/help - Show this help message
/balance - Check your balance
/stats - View your traffic statistics

💰 *How it works:*
1. Download and install the app
2. Login with your Telegram account
3. Start sharing traffic
4. Earn money automatically
5. Withdraw when you reach minimum balance

📧 Support: Contact admins for help
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    telegram_id = update.effective_user.id
    
    with get_db_context() as db:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text(
                "⚠️ You need to register in the app first!"
            )
            return
        
        balance_text = f"""
💰 *Your Balance*

Available: ${user.balance:.2f}
Total Earned: ${user.total_earned:.2f}

Minimum withdrawal: $5.00
        """
        
        await update.message.reply_text(balance_text, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    telegram_id = update.effective_user.id
    
    with get_db_context() as db:
        from traffic_share.server.services.traffic_service import TrafficService
        
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text(
                "⚠️ You need to register in the app first!"
            )
            return
        
        service = TrafficService(db)
        summary = service.get_traffic_summary(user.id)
        
        stats_text = f"""
📊 *Your Statistics*

📅 Today: {summary.daily_gb:.2f} GB | ${summary.daily_earnings:.2f}
📆 This Week: {summary.weekly_gb:.2f} GB | ${summary.weekly_earnings:.2f}
📈 This Month: {summary.monthly_gb:.2f} GB | ${summary.monthly_earnings:.2f}
🎯 Total: {summary.total_gb:.2f} GB | ${summary.total_earnings:.2f}
        """
        
        await update.message.reply_text(stats_text, parse_mode="Markdown")

"""Telegram bot for Traffic Share."""

import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TrafficShareBot:
    """Main bot class for Traffic Share."""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_ids = [int(x) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x]
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_message = f"""
🚀 Welcome to Traffic Share, {user.first_name}!

This bot helps you manage your traffic sharing account.

Available commands:
/start - Start the bot
/help - Show help
/balance - Check your balance
/status - Check your traffic status

To get started, download our mobile app and register with your Telegram account.
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 Traffic Share Bot Help

Commands:
/start - Start the bot
/help - Show this help message
/balance - Check your account balance
/status - Check your traffic sharing status

How to use:
1. Download the Traffic Share mobile app
2. Register with your Telegram account
3. Start sharing your internet traffic
4. Earn money for sharing traffic
5. Withdraw your earnings

For support, contact @admin
        """
        await update.message.reply_text(help_message)
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command."""
        user_id = update.effective_user.id
        
        # TODO: Get actual balance from database
        balance_message = f"""
💰 Your Balance

Available: $0.00
Pending: $0.00
Total Earned: $0.00

Minimum withdrawal: $5.00
        """
        await update.message.reply_text(balance_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id
        
        # TODO: Get actual status from database
        status_message = f"""
📊 Your Status

Traffic Sharing: Not Active
Sessions Today: 0
Data Shared: 0 GB
Earnings Today: $0.00

To start sharing traffic, use the mobile app.
        """
        await update.message.reply_text(status_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages."""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if it's a login code
        if message_text.isdigit() and len(message_text) == 6:
            await self.handle_login_code(update, context, message_text)
        else:
            await update.message.reply_text(
                "I don't understand that message. Use /help to see available commands."
            )
    
    async def handle_login_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE, code: str):
        """Handle login code verification."""
        user_id = update.effective_user.id
        
        # TODO: Verify code with backend API
        await update.message.reply_text(
            f"Login code {code} received. Please enter this code in the mobile app to complete login."
        )
    
    async def send_login_code(self, telegram_id: int, code: str):
        """Send login code to user."""
        try:
            await self.application.bot.send_message(
                chat_id=telegram_id,
                text=f"🔐 Your login code: {code}\n\nThis code will expire in 5 minutes."
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send login code to {telegram_id}: {e}")
            return False
    
    async def send_notification(self, telegram_id: int, message: str):
        """Send notification to user."""
        try:
            await self.application.bot.send_message(
                chat_id=telegram_id,
                text=message
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {telegram_id}: {e}")
            return False
    
    async def send_admin_notification(self, message: str):
        """Send notification to all admins."""
        for admin_id in self.admin_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=admin_id,
                    text=f"🔔 Admin Notification\n\n{message}"
                )
            except Exception as e:
                logger.error(f"Failed to send admin notification to {admin_id}: {e}")
    
    def run(self):
        """Run the bot."""
        logger.info("Starting Traffic Share Bot...")
        self.application.run_polling()

# Global bot instance
bot = TrafficShareBot()

if __name__ == "__main__":
    bot.run()

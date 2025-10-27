"""
Admin command handlers for Telegram bot
"""

from telegram import Update
from telegram.ext import ContextTypes

from traffic_share.server.config import settings
from traffic_share.server.database import get_db_context
from traffic_share.server.services.admin_service import AdminService
from traffic_share.server.logger import logger


def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    admin_ids = settings.get_admin_ids()
    return telegram_id in admin_ids


async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    telegram_id = update.effective_user.id
    
    if not is_admin(telegram_id):
        await update.message.reply_text("⛔ Access denied. Admin only.")
        return
    
    admin_text = """
🔧 *Admin Panel*

Available commands:
/users - View user statistics
/system - View system metrics

More commands coming soon...
    """
    
    await update.message.reply_text(admin_text, parse_mode="Markdown")


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command"""
    telegram_id = update.effective_user.id
    
    if not is_admin(telegram_id):
        return
    
    with get_db_context() as db:
        service = AdminService(db)
        users, total = service.get_all_users(page=1, page_size=10)
        
        users_text = f"👥 *Users Overview*\n\nTotal users: {total}\n\n"
        
        for user in users[:5]:
            users_text += f"• User {user.id}: ${user.balance:.2f}\n"
        
        await update.message.reply_text(users_text, parse_mode="Markdown")


async def system_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /system command"""
    telegram_id = update.effective_user.id
    
    if not is_admin(telegram_id):
        return
    
    with get_db_context() as db:
        service = AdminService(db)
        metrics = service.get_system_metrics()
        
        system_text = f"""
⚙️ *System Metrics*

Active Sessions: {metrics['active_sessions']}
Active Buyers: {metrics['active_buyers']}
CPU: {metrics.get('cpu_percent', 0):.1f}%
Memory: {metrics.get('memory_percent', 0):.1f}%
        """
        
        await update.message.reply_text(system_text, parse_mode="Markdown")

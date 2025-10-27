"""
Callback query handlers for inline buttons
"""

from telegram import Update
from telegram.ext import ContextTypes

from traffic_share.server.logger import logger


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    # Handle different callback data
    data = query.data
    
    if data == "refresh_balance":
        await query.edit_message_text("Balance refreshed! ✅")
    
    elif data == "view_stats":
        await query.edit_message_text("Stats coming soon... 📊")
    
    else:
        await query.edit_message_text(f"Unknown action: {data}")

"""
Message templates for bot responses
"""

from datetime import datetime


def welcome_message(username: str = None) -> str:
    """Welcome message template"""
    name = username or "there"
    return f"""
👋 Welcome {name}!

💰 *Traffic Share* - Earn money by sharing your internet traffic!

📱 Download our app
🔐 Login with Telegram
📊 Start sharing traffic
💵 Withdraw your earnings

Use /help to see all commands.
    """


def balance_message(balance: float, total_earned: float) -> str:
    """Balance message template"""
    return f"""
💰 *Your Balance*

💵 Available: ${balance:.2f}
📊 Total Earned: ${total_earned:.2f}

{'✅ You can withdraw now!' if balance >= 5 else '⏳ Minimum withdrawal: $5.00'}
    """


def stats_message(
    daily_gb: float, daily_usd: float,
    weekly_gb: float, weekly_usd: float,
    total_gb: float, total_usd: float
) -> str:
    """Stats message template"""
    return f"""
📊 *Your Statistics*

📅 *Today*
   {daily_gb:.2f} GB | ${daily_usd:.2f}

📆 *This Week*
   {weekly_gb:.2f} GB | ${weekly_usd:.2f}

🎯 *All Time*
   {total_gb:.2f} GB | ${total_usd:.2f}
    """


def payment_success_message(amount: float, tx_hash: str = None) -> str:
    """Payment success message"""
    msg = f"""
✅ *Payment Successful!*

Amount: ${amount:.2f}
Status: Completed
    """
    
    if tx_hash:
        msg += f"\nTransaction: `{tx_hash}`"
    
    return msg


def admin_notification(event: str, details: str) -> str:
    """Admin notification template"""
    return f"""
🔔 *Admin Alert*

Event: {event}
Details: {details}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
    """

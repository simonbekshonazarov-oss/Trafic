#!/usr/bin/env python3
"""
Test script for sending login code via Telegram bot
"""

import asyncio
import sys
from traffic_share.bot.bot import send_login_code
from traffic_share.server.config import settings
from traffic_share.server.logger import logger


async def test_send_code():
    """Test sending code"""
    print("=" * 60)
    print("BOT XABAR YUBORISH TESTI")
    print("=" * 60)
    
    # Show bot configuration
    print(f"\n📱 Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"👥 Admin IDs: {settings.TELEGRAM_ADMIN_IDS}")
    
    # Get telegram ID from user
    print("\n" + "=" * 60)
    telegram_id = input("Telegram ID kiriting (test uchun): ")
    
    if not telegram_id or not telegram_id.isdigit():
        print("❌ Xato: To'g'ri Telegram ID kiriting!")
        return
    
    telegram_id = int(telegram_id)
    test_code = "123456"
    
    print(f"\n📤 Kod yuborilmoqda: {telegram_id} -> {test_code}")
    print("Kutish...")
    
    # Send code
    success = await send_login_code(telegram_id, test_code)
    
    print("=" * 60)
    if success:
        print("✅ KOD MUVAFFAQIYATLI YUBORILDI!")
        print(f"Telegram ID {telegram_id} ga kod yuborildi.")
        print("Telegramingizni tekshiring!")
    else:
        print("❌ KOD YUBORISHDA XATOLIK!")
        print("\nMumkin bo'lgan sabablar:")
        print("1. Bot token noto'g'ri (.env faylida)")
        print("2. Telegram ID noto'g'ri")
        print("3. Botni /start qilmagansiz")
        print("4. Internet aloqasi yo'q")
        print("\nYechimlar:")
        print("1. .env faylida TELEGRAM_BOT_TOKEN ni tekshiring")
        print("2. Telegram'da botingizni /start buyrug'ini bosing")
        print("3. To'g'ri Telegram ID kiriting (@userinfobot dan olishingiz mumkin)")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_send_code())
    except KeyboardInterrupt:
        print("\n\n❌ Bekor qilindi")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Xatolik: {e}")
        sys.exit(1)

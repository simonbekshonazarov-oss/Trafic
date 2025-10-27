"""Bot service for server-bot communication."""

import httpx
import asyncio
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class BotService:
    """Service for communicating with Telegram bot."""
    
    def __init__(self):
        self.bot_url = os.getenv("BOT_SERVICE_URL", "http://localhost:8001")
        self.api_key = os.getenv("BOT_API_KEY", "bot_secret_key")
    
    async def send_login_code(self, telegram_id: int, code: str) -> bool:
        """Send login code to user via bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bot_url}/api/bot/send_login_code",
                    json={
                        "telegram_id": telegram_id,
                        "code": code
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send login code: {e}")
            return False
    
    async def send_notification(self, telegram_id: int, message: str) -> bool:
        """Send notification to user via bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bot_url}/api/bot/send_notification",
                    json={
                        "telegram_id": telegram_id,
                        "message": message
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False
    
    async def send_admin_notification(self, message: str) -> bool:
        """Send notification to all admins via bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bot_url}/api/bot/send_admin_notification",
                    json={"message": message},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
            return False
    
    async def update_user_balance(self, user_id: int, balance: float) -> bool:
        """Update user balance in bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bot_url}/api/bot/update_balance",
                    json={
                        "user_id": user_id,
                        "balance": balance
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to update balance: {e}")
            return False

# Global bot service instance
bot_service = BotService()

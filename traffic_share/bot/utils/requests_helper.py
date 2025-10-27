"""
Helper for making API requests from bot to server
"""

import httpx
from typing import Optional, Dict, Any

from traffic_share.server.config import settings
from traffic_share.server.logger import logger


class APIClient:
    """Client for making requests to Traffic Share API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://localhost:{settings.PORT}/api"
        self.bot_token = settings.SECRET_KEY[:32]  # Simple bot auth token
    
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request"""
        try:
            headers = {
                "X-Bot-Token": self.bot_token
            }
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}{endpoint}"
                
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, json=data, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}
    
    async def get_user_by_telegram_id(self, telegram_id: int):
        """Get user info by Telegram ID"""
        return await self.request("GET", f"/user/by_telegram/{telegram_id}")
    
    async def send_login_code(self, telegram_id: int, code: str):
        """Notify API that login code was sent"""
        return await self.request(
            "POST",
            "/bot/send_login_code",
            {"telegram_id": telegram_id, "code": code}
        )

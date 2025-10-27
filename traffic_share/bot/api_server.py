"""FastAPI server for bot to receive requests from main server."""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import asyncio
from .bot import bot

app = FastAPI(title="Traffic Share Bot API", version="1.0.0")

class LoginCodeRequest(BaseModel):
    telegram_id: int
    code: str

class NotificationRequest(BaseModel):
    telegram_id: int
    message: str

class AdminNotificationRequest(BaseModel):
    message: str

class BalanceUpdateRequest(BaseModel):
    user_id: int
    balance: float

def verify_api_key(authorization: str = Header(None)):
    """Verify API key for bot communication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    if token != "bot_secret_key":  # In production, use proper secret management
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

@app.post("/api/bot/send_login_code")
async def send_login_code(request: LoginCodeRequest, token: str = Depends(verify_api_key)):
    """Send login code to user."""
    success = await bot.send_login_code(request.telegram_id, request.code)
    if success:
        return {"success": True, "message": "Login code sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send login code")

@app.post("/api/bot/send_notification")
async def send_notification(request: NotificationRequest, token: str = Depends(verify_api_key)):
    """Send notification to user."""
    success = await bot.send_notification(request.telegram_id, request.message)
    if success:
        return {"success": True, "message": "Notification sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")

@app.post("/api/bot/send_admin_notification")
async def send_admin_notification(request: AdminNotificationRequest, token: str = Depends(verify_api_key)):
    """Send notification to all admins."""
    success = await bot.send_admin_notification(request.message)
    if success:
        return {"success": True, "message": "Admin notification sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send admin notification")

@app.post("/api/bot/update_balance")
async def update_balance(request: BalanceUpdateRequest, token: str = Depends(verify_api_key)):
    """Update user balance in bot."""
    # This would update the user's balance display in bot
    return {"success": True, "message": "Balance updated"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bot-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

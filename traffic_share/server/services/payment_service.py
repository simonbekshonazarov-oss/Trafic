"""Payment service using Cryptomus API."""

import httpx
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime
import os

from traffic_share.core.exceptions import PaymentError, ExternalServiceError

class CryptomusPaymentService:
    """Cryptomus payment service implementation."""
    
    def __init__(self):
        self.merchant_id = os.getenv("CRYPTOMUS_MERCHANT_ID")
        self.api_key = os.getenv("CRYPTOMUS_API_KEY")
        self.webhook_secret = os.getenv("CRYPTOMUS_WEBHOOK_SECRET")
        self.base_url = "https://api.cryptomus.com/v1"
        
        if not all([self.merchant_id, self.api_key]):
            raise PaymentError("Cryptomus credentials not configured")
    
    def _generate_signature(self, data: str) -> str:
        """Generate signature for Cryptomus API request."""
        return hmac.new(
            self.api_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def create_payment(self, amount: float, currency: str = "USD", 
                           order_id: str = None, description: str = None) -> Dict[str, Any]:
        """Create a new payment."""
        if not order_id:
            order_id = f"traffic_share_{int(datetime.utcnow().timestamp())}"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "order_id": order_id,
            "url_return": "https://your-domain.com/payment/return",
            "url_callback": "https://your-domain.com/api/webhook/cryptomus",
            "is_payment_multiple": False,
            "lifetime": 7200,  # 2 hours
            "to_currency": "USDT",
            "subtract": 0,
            "accuracy": 6,
            "additional_data": description or "Traffic Share Withdrawal"
        }
        
        data = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(data)
        
        headers = {
            "merchant": self.merchant_id,
            "sign": signature,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment",
                    data=data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Payment creation failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status."""
        payload = {"uuid": payment_id}
        data = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(data)
        
        headers = {
            "merchant": self.merchant_id,
            "sign": signature,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment/info",
                    data=data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Payment status check failed: {str(e)}")
    
    async def create_payout(self, amount: float, currency: str, 
                          address: str, order_id: str = None) -> Dict[str, Any]:
        """Create a payout to user."""
        if not order_id:
            order_id = f"payout_{int(datetime.utcnow().timestamp())}"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "address": address,
            "order_id": order_id,
            "is_subtract": True,
            "is_refill": False
        }
        
        data = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(data)
        
        headers = {
            "merchant": self.merchant_id,
            "sign": signature,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payout",
                    data=data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Payout creation failed: {str(e)}")
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature."""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook."""
        # Verify webhook signature
        # This would be implemented based on your webhook handling
        
        payment_data = payload.get("data", {})
        status = payment_data.get("status")
        order_id = payment_data.get("order_id")
        
        return {
            "status": status,
            "order_id": order_id,
            "processed": True
        }

# Global payment service instance
payment_service = CryptomusPaymentService()

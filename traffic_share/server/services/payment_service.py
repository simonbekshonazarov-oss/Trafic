"""
Payment service - handles withdrawals via Cryptomus
"""

import hashlib
import base64
import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import httpx

from traffic_share.server.models import Payment, User
from traffic_share.server.schemas import (
    WithdrawRequest, WithdrawResponse,
    PaymentStatusResponse
)
from traffic_share.core.exceptions import (
    ResourceNotFoundError, InsufficientBalanceError,
    PaymentError, ValidationError
)
from traffic_share.server.config import settings
from traffic_share.server.logger import logger
from traffic_share.server.utils import create_audit_log


class CryptomusPaymentService:
    """Cryptomus payment gateway integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_url = settings.CRYPTOMUS_API_URL
        self.api_key = settings.CRYPTOMUS_API_KEY
        self.merchant_id = settings.CRYPTOMUS_MERCHANT_ID
    
    def _generate_signature(self, data: dict) -> str:
        """Generate request signature for Cryptomus API"""
        # Convert data to JSON string
        json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        # Encode to base64
        encoded_data = base64.b64encode(json_data.encode()).decode()
        
        # Create signature: md5(base64(data) + api_key)
        signature_string = encoded_data + self.api_key
        signature = hashlib.md5(signature_string.encode()).hexdigest()
        
        return signature
    
    async def create_payout(
        self, 
        user_id: int, 
        request: WithdrawRequest
    ) -> WithdrawResponse:
        """Create payout request via Cryptomus"""
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User not found")
        
        # Validate amount
        if request.amount < settings.MIN_WITHDRAWAL_AMOUNT:
            raise ValidationError(
                f"Minimum withdrawal amount is ${settings.MIN_WITHDRAWAL_AMOUNT}"
            )
        
        if request.amount > settings.MAX_WITHDRAWAL_AMOUNT:
            raise ValidationError(
                f"Maximum withdrawal amount is ${settings.MAX_WITHDRAWAL_AMOUNT}"
            )
        
        # Check balance
        if user.balance < request.amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: ${user.balance:.2f}"
            )
        
        # Create payment record
        payment = Payment(
            user_id=user_id,
            amount=request.amount,
            currency="USD",
            method=request.method,
            target=request.target,
            status="pending"
        )
        
        self.db.add(payment)
        self.db.flush()  # Get payment ID
        
        # Reserve balance (deduct immediately, will refund if payout fails)
        user.balance -= request.amount
        
        try:
            # Prepare Cryptomus API request
            order_id = f"payout_{payment.id}_{int(datetime.utcnow().timestamp())}"
            
            payout_data = {
                "amount": str(request.amount),
                "currency": "USD",
                "network": "TRX",  # USDT TRC20 as default
                "order_id": order_id,
                "address": request.target,
                "is_subtract": "0"  # Don't subtract fee from amount
            }
            
            # Generate signature
            signature = self._generate_signature(payout_data)
            
            # Make API request
            headers = {
                "merchant": self.merchant_id,
                "sign": signature,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/payout",
                    json=payout_data,
                    headers=headers,
                    timeout=30.0
                )
                
                result = response.json()
                
                if response.status_code == 200 and result.get("state") == 0:
                    # Success
                    payout_info = result.get("result", {})
                    
                    payment.status = "processing"
                    payment.tx_reference = payout_info.get("uuid")
                    payment.processed_at = datetime.utcnow()
                    
                    self.db.commit()
                    
                    logger.info(
                        f"Payout created for user {user_id}: "
                        f"${request.amount} to {request.target}"
                    )
                    
                    create_audit_log(
                        self.db,
                        action="create_payout",
                        entity_type="payment",
                        entity_id=payment.id,
                        user_id=user_id,
                        details={
                            "amount": request.amount,
                            "target": request.target,
                            "order_id": order_id
                        }
                    )
                    
                    return WithdrawResponse(
                        payment_id=payment.id,
                        status="processing",
                        message="Payout request submitted successfully"
                    )
                else:
                    # API error
                    error_msg = result.get("message", "Unknown error")
                    raise PaymentError(f"Cryptomus API error: {error_msg}")
        
        except Exception as e:
            # Refund balance on error
            user.balance += request.amount
            payment.status = "failed"
            payment.error_message = str(e)
            self.db.commit()
            
            logger.error(f"Payout failed for user {user_id}: {str(e)}")
            
            raise PaymentError(f"Failed to create payout: {str(e)}")
    
    def get_payment_status(self, payment_id: int, user_id: int = None) -> PaymentStatusResponse:
        """Get payment status"""
        query = self.db.query(Payment).filter(Payment.id == payment_id)
        
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        
        payment = query.first()
        
        if not payment:
            raise ResourceNotFoundError("Payment not found")
        
        return PaymentStatusResponse.from_orm(payment)
    
    def handle_webhook(self, payload: dict) -> bool:
        """
        Handle Cryptomus webhook for payout status update
        """
        try:
            # Extract order_id to find payment
            order_id = payload.get("order_id", "")
            
            # Parse payment_id from order_id (format: payout_{payment_id}_{timestamp})
            if not order_id.startswith("payout_"):
                logger.warning(f"Invalid order_id format: {order_id}")
                return False
            
            parts = order_id.split("_")
            if len(parts) < 3:
                logger.warning(f"Cannot parse payment_id from order_id: {order_id}")
                return False
            
            payment_id = int(parts[1])
            
            # Get payment
            payment = self.db.query(Payment).filter(
                Payment.id == payment_id
            ).first()
            
            if not payment:
                logger.warning(f"Payment {payment_id} not found for webhook")
                return False
            
            # Update payment based on status
            status = payload.get("status", "")
            
            if status == "paid" or status == "paid_over":
                # Payout completed
                payment.status = "completed"
                payment.completed_at = datetime.utcnow()
                payment.tx_hash = payload.get("txid")
                
                logger.info(f"Payout {payment_id} completed successfully")
            
            elif status == "cancel" or status == "fail":
                # Payout failed - refund user balance
                payment.status = "failed"
                payment.error_message = payload.get("payment_status", "Unknown error")
                
                # Refund balance
                user = self.db.query(User).filter(User.id == payment.user_id).first()
                if user:
                    user.balance += payment.amount
                
                logger.warning(f"Payout {payment_id} failed, balance refunded")
            
            elif status == "process":
                payment.status = "processing"
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return False


class PaymentService:
    """Main payment service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cryptomus = CryptomusPaymentService(db)
    
    async def request_withdrawal(
        self, 
        user_id: int, 
        request: WithdrawRequest
    ) -> WithdrawResponse:
        """Request withdrawal"""
        return await self.cryptomus.create_payout(user_id, request)
    
    def get_payment_status(
        self, 
        payment_id: int, 
        user_id: int = None
    ) -> PaymentStatusResponse:
        """Get payment status"""
        return self.cryptomus.get_payment_status(payment_id, user_id)
    
    def handle_webhook(self, payload: dict) -> bool:
        """Handle payment webhook"""
        return self.cryptomus.handle_webhook(payload)

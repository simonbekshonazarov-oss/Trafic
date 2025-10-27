"""
Payment and balance routes
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from traffic_share.server.database import get_db
from traffic_share.server.dependencies import get_current_user
from traffic_share.server.models import User
from traffic_share.server.schemas import (
    BalanceResponse, WithdrawRequest, WithdrawResponse,
    PaymentStatusResponse, StandardResponse
)
from traffic_share.server.services.user_service import UserService
from traffic_share.server.services.payment_service import PaymentService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(tags=["Balance & Payments"])


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user balance"""
    try:
        service = UserService(db)
        balance_info = service.get_user_balance(current_user.id)
        
        return BalanceResponse(**balance_info)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/withdraw/request", response_model=WithdrawResponse)
async def request_withdrawal(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request withdrawal/payout"""
    try:
        service = PaymentService(db)
        return await service.request_withdrawal(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/withdraw/status/{payment_id}", response_model=PaymentStatusResponse)
async def get_withdrawal_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get withdrawal status"""
    try:
        service = PaymentService(db)
        return service.get_payment_status(payment_id, current_user.id)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/webhook/cryptomus", response_model=StandardResponse)
async def cryptomus_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Cryptomus payment webhook"""
    try:
        payload = await request.json()
        
        service = PaymentService(db)
        success = service.handle_webhook(payload)
        
        return StandardResponse(
            ok=success,
            message="Webhook processed" if success else "Webhook processing failed"
        )
    except Exception as e:
        return StandardResponse(ok=False, message=str(e))

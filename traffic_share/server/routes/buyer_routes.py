"""
Buyer routes - for traffic consumers
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List

from traffic_share.server.database import get_db
from traffic_share.server.dependencies import get_current_buyer
from traffic_share.server.models import Buyer, BuyerToken
from traffic_share.server.schemas import (
    PullPacketsRequest, PullPacketsResponse,
    UpdatePacketStatusRequest, StandardResponse
)
from traffic_share.server.services.buyer_service import BuyerService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(prefix="/buyer", tags=["Buyer"])


@router.post("/packets/pull", response_model=PullPacketsResponse)
async def pull_packets(
    request: PullPacketsRequest,
    buyer_info: tuple[Buyer, BuyerToken] = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """Pull available traffic packets"""
    try:
        buyer, token = buyer_info
        service = BuyerService(db)
        
        return service.pull_packets(buyer.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/packets/{uuid}/status", response_model=StandardResponse)
async def update_packet_status(
    uuid: str = Path(...),
    request: UpdatePacketStatusRequest = ...,
    buyer_info: tuple[Buyer, BuyerToken] = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """Update packet status (in_progress, completed, failed)"""
    try:
        buyer, token = buyer_info
        service = BuyerService(db)
        
        success = service.update_packet_status(buyer.id, uuid, request)
        
        return StandardResponse(
            ok=success,
            message="Packet status updated"
        )
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/me/allocations")
async def get_my_allocations(
    buyer_info: tuple[Buyer, BuyerToken] = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """Get current allocations"""
    try:
        buyer, token = buyer_info
        service = BuyerService(db)
        
        return service.get_buyer_allocations(buyer.id)
    except TrafficShareException as e:
        raise create_http_exception(e)

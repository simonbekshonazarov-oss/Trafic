"""
Server-level yordamchi funksiyalar
"""

import json
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from traffic_share.server.models import AuditLog, SystemMetric
from .jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def bytes_to_gb(bytes_count: int) -> float:
    """Baytlarni gigabaytga aylantirish"""
    return round(bytes_count / (1024 ** 3), 6)


def gb_to_bytes(gb: float) -> int:
    """Gigabaytlarni baytga aylantirish"""
    return int(gb * (1024 ** 3))


def calculate_earnings(bytes_count: int, price_per_gb: float) -> float:
    """Trafik hajmidan daromadni hisoblash"""
    gb = bytes_to_gb(bytes_count)
    return round(gb * price_per_gb, 2)


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    user_id: int | None = None,
    admin_id: int | None = None,
    buyer_id: int | None = None,
    details: Dict[str, Any] | None = None,
    ip_address: str | None = None
):
    """Audit log yozuvini yaratish"""
    audit_log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        admin_id=admin_id,
        buyer_id=buyer_id,
        details=json.dumps(details) if details else None,
        ip_address=ip_address
    )
    db.add(audit_log)
    db.commit()


def record_metric(
    db: Session,
    metric_name: str,
    metric_value: float,
    metric_unit: str | None = None,
    tags: Dict[str, Any] | None = None
):
    """Tizim metrikasini saqlash"""
    metric = SystemMetric(
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        tags=json.dumps(tags) if tags else None
    )
    db.add(metric)
    db.commit()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str | None:
    """Datetime ni matnga formatlash"""
    if not dt:
        return None
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime | None:
    """Matnni datetime ga parse qilish"""
    if not dt_str:
        return None
    return datetime.strptime(dt_str, format_str)


def get_client_ip(request) -> str:
    """HTTP so'rovdan mijoz IP manzilini ajratib olish"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else "unknown"


def paginate_query(query, page: int = 1, page_size: int = 50):
    """SQLAlchemy query uchun paginatsiya"""
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total_count, total_pages


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100):
    """Paginatsiya parametrlarini tekshirish va normallashtirish"""
    page = max(1, page)
    page_size = max(1, min(page_size, max_page_size))
    return page, page_size


__all__ = [
    "bytes_to_gb",
    "gb_to_bytes",
    "calculate_earnings",
    "create_audit_log",
    "record_metric",
    "format_datetime",
    "parse_datetime",
    "get_client_ip",
    "paginate_query",
    "validate_pagination_params",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]

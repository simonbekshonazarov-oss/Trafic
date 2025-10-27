"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from traffic_share.core.constants import UserStatus, SessionStatus, PackageStatus, PaymentStatus, PaymentMethod

# Base schemas
class BaseResponse(BaseModel):
    """Base response schema."""
    success: bool = True
    message: str = "Success"

class ErrorResponse(BaseResponse):
    """Error response schema."""
    success: bool = False
    error_code: Optional[str] = None

# Auth schemas
class RegisterRequest(BaseModel):
    """User registration request."""
    telegram_id: int
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class LoginCodeRequest(BaseModel):
    """Login code request."""
    telegram_id: int

class VerifyCodeRequest(BaseModel):
    """Code verification request."""
    telegram_id: int
    code: str

class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# User schemas
class UserResponse(BaseModel):
    """User profile response."""
    id: int
    telegram_id: int
    username: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    balance: float
    is_verified: bool
    is_active: bool
    status: UserStatus
    created_at: datetime
    last_active: Optional[datetime]

class UserUpdateRequest(BaseModel):
    """User profile update request."""
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class DeviceRegisterRequest(BaseModel):
    """Device registration request."""
    device_id: str
    os: str
    ip: str

class DeviceResponse(BaseModel):
    """Device response."""
    id: int
    device_id: str
    os: str
    ip_address: Optional[str]
    last_active: datetime
    created_at: datetime

# Traffic schemas
class TrafficStartRequest(BaseModel):
    """Traffic session start request."""
    device_id: str
    local_ip: str
    public_ip: str
    client_version: str

class TrafficStartResponse(BaseModel):
    """Traffic session start response."""
    session_id: str
    success: bool = True

class TrafficUpdateRequest(BaseModel):
    """Traffic update request."""
    session_id: str
    bytes_tx: int
    bytes_rx: int
    interval_seconds: int

class TrafficStopRequest(BaseModel):
    """Traffic session stop request."""
    session_id: str
    final_bytes_tx: int
    final_bytes_rx: int

class TrafficSessionResponse(BaseModel):
    """Traffic session response."""
    id: int
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: SessionStatus
    bytes_tx: int
    bytes_rx: int
    bytes_total: int
    start_ip: Optional[str]
    end_ip: Optional[str]

class TrafficSummaryResponse(BaseModel):
    """Traffic summary response."""
    daily: float
    weekly: float
    monthly: float
    total: float
    sessions_count: int

# Balance and Payment schemas
class BalanceResponse(BaseModel):
    """Balance response."""
    available: float
    pending: float
    currency: str = "USD"

class WithdrawalRequest(BaseModel):
    """Withdrawal request."""
    amount: float
    method: PaymentMethod
    target: str

class WithdrawalResponse(BaseModel):
    """Withdrawal response."""
    payment_id: int
    status: PaymentStatus
    amount: float
    method: PaymentMethod
    target: str

class PaymentResponse(BaseModel):
    """Payment response."""
    id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    target: str
    tx_reference: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

# Buyer schemas
class BuyerCreateRequest(BaseModel):
    """Buyer creation request."""
    name: str
    contact: Optional[str] = None
    region: Optional[str] = None

class BuyerResponse(BaseModel):
    """Buyer response."""
    id: int
    name: str
    contact: Optional[str]
    region: Optional[str]
    is_active: bool
    created_at: datetime

class BuyerTokenCreateRequest(BaseModel):
    """Buyer token creation request."""
    expires_at: Optional[datetime] = None
    description: Optional[str] = None

class BuyerTokenResponse(BaseModel):
    """Buyer token response."""
    token: str
    expires_at: Optional[datetime]
    description: Optional[str]

class BuyerTokenListResponse(BaseModel):
    """Buyer token list response."""
    id: int
    description: Optional[str]
    is_revoked: bool
    created_at: datetime
    expires_at: Optional[datetime]

# Package schemas
class PackageCreateRequest(BaseModel):
    """Package creation request."""
    packages: List[dict]

class PackageResponse(BaseModel):
    """Package response."""
    id: int
    uuid: str
    user_id: int
    ip_address: str
    size_bytes: int
    status: PackageStatus
    assigned_buyer_id: Optional[int]
    assigned_at: Optional[datetime]
    bytes_sent: int
    created_at: datetime

class PackageAllocationRequest(BaseModel):
    """Package allocation request."""
    max_count: int = 1
    region: Optional[str] = None

class PackageStatusUpdateRequest(BaseModel):
    """Package status update request."""
    status: PackageStatus
    bytes_sent: Optional[int] = 0

# Admin schemas
class AdminUserResponse(BaseModel):
    """Admin user response."""
    id: int
    telegram_id: int
    username: Optional[str]
    balance: float
    is_active: bool
    status: UserStatus
    created_at: datetime
    last_active: Optional[datetime]

class AdminNotificationRequest(BaseModel):
    """Admin notification request."""
    target: str  # all, active, region:US
    message: str

class AdminReportResponse(BaseModel):
    """Admin report response."""
    date: str
    active_users: int
    total_traffic_gb: float
    total_payments: float
    new_users: int
    active_sessions: int

class AdminMetricsResponse(BaseModel):
    """Admin metrics response."""
    requests_per_minute: int
    error_rate: float
    active_connections: int
    memory_usage: float
    cpu_usage: float
    uptime_seconds: int

# System schemas
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str

class VersionResponse(BaseModel):
    """Version response."""
    api_version: str
    app_latest: str
    force_update: bool = False

# Bot schemas
class BotLoginCodeRequest(BaseModel):
    """Bot login code request."""
    telegram_id: int
    code: str

class BotNotificationRequest(BaseModel):
    """Bot notification request."""
    type: str
    payload: dict

class BotBalanceUpdateRequest(BaseModel):
    """Bot balance update request."""
    user_id: int
    balance: float

class BotLiveTrafficRequest(BaseModel):
    """Bot live traffic request."""
    user_id: int
    session_id: str
    bytes: int

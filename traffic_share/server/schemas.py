"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


# ==================== App Update Schemas ====================

class CheckUpdateRequest(BaseModel):
    platform: str = Field(..., description="android or ios")
    current_version: str = Field(..., description="Current app version (e.g., 1.0.0+1)")
    device_id: Optional[str] = None


class CheckUpdateResponse(BaseModel):
    update_available: bool
    latest_version: Optional[str] = None
    version_code: Optional[int] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    release_notes: Optional[str] = None
    is_mandatory: bool = False
    message: str


class AppVersionResponse(BaseModel):
    ok: bool
    version: Optional[str] = None
    version_code: Optional[int] = None
    platform: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    release_notes: Optional[str] = None
    is_mandatory: bool = False
    published_at: Optional[datetime] = None
    message: Optional[str] = None


# ==================== Auth Schemas ====================

class RegisterRequest(BaseModel):
    telegram_id: int
    phone: Optional[str] = None
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    user_id: int
    message: str


class LoginCodeRequest(BaseModel):
    telegram_id: int


class LoginCodeResponse(BaseModel):
    ok: bool


class VerifyCodeRequest(BaseModel):
    telegram_id: int
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== User Schemas ====================

class UserProfile(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    balance: float
    total_earned: float
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class DeviceRegisterRequest(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    os: str
    app_version: Optional[str] = None
    ip: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    device_id: str
    device_name: Optional[str]
    os: Optional[str]
    last_ip: Optional[str]
    last_active_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


# ==================== Traffic Schemas ====================

class TrafficStartRequest(BaseModel):
    device_id: str
    local_ip: Optional[str] = None
    public_ip: Optional[str] = None
    client_version: Optional[str] = None


class TrafficStartResponse(BaseModel):
    session_id: str
    ok: bool


class TrafficUpdateRequest(BaseModel):
    session_id: str
    bytes_tx: int = Field(ge=0)
    bytes_rx: int = Field(ge=0)
    interval_seconds: Optional[int] = None


class TrafficUpdateResponse(BaseModel):
    ok: bool


class TrafficStopRequest(BaseModel):
    session_id: str
    final_bytes_tx: int = Field(ge=0)
    final_bytes_rx: int = Field(ge=0)


class TrafficStopResponse(BaseModel):
    ok: bool
    earnings: Optional[float] = None


class TrafficSessionResponse(BaseModel):
    id: int
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    bytes_total: int
    earnings: float
    status: str
    
    class Config:
        from_attributes = True


class TrafficSummaryResponse(BaseModel):
    daily_gb: float
    weekly_gb: float
    monthly_gb: float
    total_gb: float
    daily_earnings: float
    weekly_earnings: float
    monthly_earnings: float
    total_earnings: float


# ==================== Balance & Payment Schemas ====================

class BalanceResponse(BaseModel):
    available: float
    pending: float
    total_earned: float
    currency: str = "USD"


class WithdrawRequest(BaseModel):
    amount: float = Field(gt=0)
    method: str = "cryptomus"
    target: str  # Wallet address


class WithdrawResponse(BaseModel):
    payment_id: int
    status: str
    message: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    payment_id: int
    amount: float
    status: str
    method: str
    tx_reference: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== Buyer Schemas ====================

class CreateBuyerRequest(BaseModel):
    name: str
    contact: Optional[str] = None
    region: Optional[str] = None


class BuyerResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    region: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateBuyerTokenRequest(BaseModel):
    buyer_id: int
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class BuyerTokenResponse(BaseModel):
    token: str  # Returned only once!
    token_id: int
    description: Optional[str]
    expires_at: Optional[datetime]


class BuyerTokenMetadata(BaseModel):
    id: int
    description: Optional[str]
    is_revoked: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Package Schemas ====================

class PackageCreate(BaseModel):
    uuid: str
    user_id: int
    ip: str
    size_bytes: int


class BulkCreatePackagesRequest(BaseModel):
    packages: List[PackageCreate]


class BulkCreatePackagesResponse(BaseModel):
    created: int
    errors: List[str] = []


class PackageResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    ip: str
    size_bytes: int
    status: str
    assigned_buyer_id: Optional[int]
    bytes_sent: int
    allocated_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PullPacketsRequest(BaseModel):
    max_count: int = Field(default=1, ge=1, le=10)
    region: Optional[str] = None


class PacketInfo(BaseModel):
    uuid: str
    user_id: int
    ip: str
    size_bytes: int
    assigned_at: datetime


class PullPacketsResponse(BaseModel):
    packages: List[PacketInfo]


class UpdatePacketStatusRequest(BaseModel):
    status: str  # in_progress, completed, failed
    bytes_sent: Optional[int] = None


class AssignPackageRequest(BaseModel):
    buyer_id: int


class BuyerUsageResponse(BaseModel):
    buyer_id: int
    total_assigned: int
    active: int
    completed: int
    failed: int
    total_bytes_sent: int


# ==================== Admin Schemas ====================

class CreateAdminRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    role: str = "admin"


class UserListResponse(BaseModel):
    users: List[UserProfile]
    total: int
    page: int
    page_size: int


class BanUserRequest(BaseModel):
    reason: Optional[str] = None


class NotifyRequest(BaseModel):
    target: str = "all"  # all, active, region:XX, user_id:123
    message: str
    title: Optional[str] = None


class DailyReportResponse(BaseModel):
    date: str
    total_users: int
    active_users: int
    new_users: int
    total_traffic_gb: float
    total_earnings: float
    total_payouts: float
    active_sessions: int


class MetricsResponse(BaseModel):
    requests_per_minute: float
    active_sessions: int
    active_buyers: int
    db_connections: int
    redis_connected: bool
    uptime_seconds: int


# ==================== System Schemas ====================

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class VersionResponse(BaseModel):
    api_version: str
    app_latest: str
    force_update: bool
    update_url: Optional[str] = None


class LogQueryRequest(BaseModel):
    level: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


# ==================== Webhook Schemas ====================

class CryptomusWebhookPayload(BaseModel):
    """Cryptomus webhook payload structure"""
    order_id: str
    uuid: str
    status: str
    payment_status: str
    payer_currency: str
    payer_amount: str
    currency: str
    amount: str
    txid: Optional[str] = None
    network: Optional[str] = None


# ==================== Common Schemas ====================

class StandardResponse(BaseModel):
    ok: bool
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int

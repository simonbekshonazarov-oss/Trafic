"""Constants and configuration values for the Traffic Share application."""

from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PackageStatus(str, Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVOKED = "revoked"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CRYPTOMUS = "cryptomus"
    PAYPAL = "paypal"

# API Response Messages
MESSAGES = {
    "user_created": "User created successfully",
    "login_code_sent": "Login code sent to your Telegram",
    "login_successful": "Login successful",
    "invalid_credentials": "Invalid credentials",
    "user_not_found": "User not found",
    "session_started": "Traffic session started",
    "session_stopped": "Traffic session stopped",
    "traffic_updated": "Traffic data updated",
    "withdrawal_requested": "Withdrawal request submitted",
    "payment_completed": "Payment completed successfully",
    "region_not_allowed": "Your region is not allowed",
    "insufficient_balance": "Insufficient balance",
    "invalid_token": "Invalid or expired token",
    "rate_limit_exceeded": "Rate limit exceeded",
    "package_allocated": "Package allocated successfully",
    "package_status_updated": "Package status updated",
}

# Rate Limiting
RATE_LIMITS = {
    "auth_requests": 5,  # per minute
    "traffic_updates": 60,  # per minute
    "buyer_pull": 10,  # per minute
    "general_api": 100,  # per minute
}

# Traffic Configuration
TRAFFIC_CONFIG = {
    "min_session_duration": 60,  # seconds
    "max_session_duration": 86400,  # 24 hours
    "update_interval": 10,  # seconds
    "cleanup_interval": 300,  # 5 minutes
}

# Cryptomus Configuration
CRYPTOMUS_CONFIG = {
    "base_url": "https://api.cryptomus.com/v1",
    "timeout": 30,
    "retry_attempts": 3,
}

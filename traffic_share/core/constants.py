"""
Core constants for Traffic Share platform
"""

# User roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_BUYER = "buyer"

# Traffic session statuses
SESSION_STATUS_ACTIVE = "active"
SESSION_STATUS_COMPLETED = "completed"
SESSION_STATUS_FAILED = "failed"

# Package statuses
PACKAGE_STATUS_AVAILABLE = "available"
PACKAGE_STATUS_ALLOCATED = "allocated"
PACKAGE_STATUS_IN_PROGRESS = "in_progress"
PACKAGE_STATUS_COMPLETED = "completed"
PACKAGE_STATUS_FAILED = "failed"
PACKAGE_STATUS_REVOKED = "revoked"

# Payment statuses
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_PROCESSING = "processing"
PAYMENT_STATUS_COMPLETED = "completed"
PAYMENT_STATUS_FAILED = "failed"
PAYMENT_STATUS_CANCELLED = "cancelled"

# Payment methods
PAYMENT_METHOD_CRYPTOMUS = "cryptomus"

# Regions
ALLOWED_REGIONS = ["US", "EU", "UK", "CA", "AU"]
REGION_US = "US"
REGION_EU = "EU"

# Token expiry
TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30
LOGIN_CODE_EXPIRE_MINUTES = 5

# Rate limiting
RATE_LIMIT_AUTH = "10/minute"
RATE_LIMIT_TRAFFIC_UPDATE = "100/minute"
RATE_LIMIT_BUYER_PULL = "10/minute"
RATE_LIMIT_DEFAULT = "60/minute"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Traffic pricing
PRICE_PER_GB = 0.50  # USD per GB
MIN_WITHDRAWAL_AMOUNT = 5.0  # Minimum USD
MAX_WITHDRAWAL_AMOUNT = 1000.0  # Maximum USD

# Package allocation
PACKAGE_ALLOCATION_TTL_SECONDS = 60  # Time before allocated package expires
MAX_PACKAGES_PER_REQUEST = 10

# File upload limits
MAX_UPLOAD_SIZE_MB = 10

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_ROTATION_SIZE_MB = 10
LOG_BACKUP_COUNT = 5

# Database
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Redis
REDIS_KEY_PREFIX = "traffic_share:"
REDIS_SESSION_EXPIRE = 86400  # 24 hours

# API versioning
API_VERSION = "v1"
API_PREFIX = "/api"

# System
APP_NAME = "Traffic Share"
APP_VERSION = "1.0.0"
MIN_APP_VERSION = "1.0.0"  # Minimum app version required

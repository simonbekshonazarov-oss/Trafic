"""
SQLAlchemy ORM Models - Database table definitions
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, BigInteger, Enum, Index
)
from sqlalchemy.orm import relationship
import enum

from traffic_share.server.database import Base


class User(Base):
    """User model - traffic providers"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    balance = Column(Float, default=0.0, nullable=False)
    total_earned = Column(Float, default=0.0, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    traffic_sessions = relationship("TrafficSession", back_populates="user")
    devices = relationship("Device", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    login_codes = relationship("LoginCode", back_populates="user")
    
    __table_args__ = (
        Index('idx_telegram_id', 'telegram_id'),
        Index('idx_is_active', 'is_active'),
    )


class Admin(Base):
    """Admin users"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    role = Column(String(50), default="admin", nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LoginCode(Base):
    """Login verification codes"""
    __tablename__ = "login_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(10), nullable=False, index=True)
    
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="login_codes")
    
    __table_args__ = (
        Index('idx_code_expires', 'code', 'expires_at'),
    )


class Device(Base):
    """User devices"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    device_id = Column(String(255), unique=True, nullable=False, index=True)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # android, ios, windows, etc
    os_version = Column(String(100), nullable=True)
    app_version = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="devices")
    traffic_sessions = relationship("TrafficSession", back_populates="device")


class TrafficSessionStatus(enum.Enum):
    """Traffic session status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class TrafficSession(Base):
    """Traffic sharing sessions"""
    __tablename__ = "traffic_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    session_uuid = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(Enum(TrafficSessionStatus), default=TrafficSessionStatus.ACTIVE, nullable=False)
    
    bytes_uploaded = Column(BigInteger, default=0, nullable=False)
    bytes_downloaded = Column(BigInteger, default=0, nullable=False)
    total_bytes = Column(BigInteger, default=0, nullable=False)
    
    earnings = Column(Float, default=0.0, nullable=False)
    
    ip_address = Column(String(100), nullable=True)
    region = Column(String(10), nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="traffic_sessions")
    device = relationship("Device", back_populates="traffic_sessions")
    traffic_logs = relationship("TrafficLog", back_populates="session")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_session_uuid', 'session_uuid'),
    )


class TrafficLog(Base):
    """Detailed traffic logs"""
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("traffic_sessions.id"), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    bytes_transferred = Column(BigInteger, nullable=False)
    connection_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    session = relationship("TrafficSession", back_populates="traffic_logs")
    
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )


class Buyer(Base):
    """Buyers who purchase traffic"""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    company = Column(String(255), nullable=True)
    
    api_key = Column(String(100), unique=True, nullable=False, index=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tokens = relationship("BuyerToken", back_populates="buyer")
    package_allocations = relationship("PackageAllocation", back_populates="buyer")


class BuyerToken(Base):
    """API tokens for buyers"""
    __tablename__ = "buyer_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="tokens")


class PackageStatus(enum.Enum):
    """Package status enum"""
    PENDING = "pending"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Package(Base):
    """Traffic packages"""
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    package_uuid = Column(String(100), unique=True, nullable=False, index=True)
    
    size_gb = Column(Float, nullable=False)
    region = Column(String(10), nullable=False)
    
    status = Column(Enum(PackageStatus), default=PackageStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    allocated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    allocations = relationship("PackageAllocation", back_populates="package")
    
    __table_args__ = (
        Index('idx_status_region', 'status', 'region'),
    )


class PackageAllocation(Base):
    """Package allocation history"""
    __tablename__ = "package_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    
    bytes_used = Column(BigInteger, default=0, nullable=False)
    allocated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    package = relationship("Package", back_populates="allocations")
    buyer = relationship("Buyer", back_populates="package_allocations")


class PaymentStatus(enum.Enum):
    """Payment status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Payment(Base):
    """Payments and withdrawals"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cryptomus
    payment_address = Column(String(255), nullable=True)
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    external_id = Column(String(255), nullable=True, index=True)
    transaction_hash = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_external_id', 'external_id'),
    )


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    """Audit trail for important actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    
    user_id = Column(Integer, nullable=True)
    admin_id = Column(Integer, nullable=True)
    buyer_id = Column(Integer, nullable=True)
    
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_action_created', 'action', 'created_at'),
    )


class SystemMetrics(Base):
    """System metrics and statistics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_metric_timestamp', 'metric_name', 'timestamp'),
    )


class AppVersion(Base):
    """App version management for OTA updates"""
    __tablename__ = "app_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    version = Column(String(50), nullable=False, unique=True, index=True)
    version_code = Column(Integer, nullable=False, unique=True)
    
    platform = Column(String(20), nullable=False)  # android, ios
    min_supported_version = Column(String(50), nullable=True)
    
    download_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    checksum = Column(String(255), nullable=True)
    
    release_notes = Column(Text, nullable=True)
    
    is_mandatory = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_platform_version', 'platform', 'version_code'),
        Index('idx_active', 'is_active', 'platform'),
    )

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
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=True)


class LoginCode(Base):
    """Login verification codes"""
    __tablename__ = "login_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(10), nullable=False, index=True)
    
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="login_codes")
    
    __table_args__ = (
        Index('idx_code_user', 'code', 'user_id'),
        Index('idx_expires_at', 'expires_at'),
    )


class Device(Base):
    """User devices/sessions"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(255), unique=True, nullable=False, index=True)
    
    device_name = Column(String(255), nullable=True)
    os = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)
    
    last_ip = Column(String(50), nullable=True)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="devices")


class TrafficSession(Base):
    """Traffic sharing sessions"""
    __tablename__ = "traffic_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(255), nullable=True)
    
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    start_ip = Column(String(50), nullable=True)
    region = Column(String(10), nullable=True)
    
    bytes_tx = Column(BigInteger, default=0, nullable=False)  # Transmitted
    bytes_rx = Column(BigInteger, default=0, nullable=False)  # Received
    bytes_total = Column(BigInteger, default=0, nullable=False)
    
    status = Column(String(20), default="active", nullable=False)  # active, completed, failed
    
    earnings = Column(Float, default=0.0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="traffic_sessions")
    traffic_logs = relationship("TrafficLog", back_populates="session")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_session_id', 'session_id'),
    )


class TrafficLog(Base):
    """Detailed traffic logs (periodic updates)"""
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("traffic_sessions.id"), nullable=False)
    
    bytes_tx = Column(BigInteger, default=0, nullable=False)
    bytes_rx = Column(BigInteger, default=0, nullable=False)
    interval_seconds = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    session = relationship("TrafficSession", back_populates="traffic_logs")
    
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )


class Buyer(Base):
    """Traffic buyers/consumers"""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=True)
    region = Column(String(10), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tokens = relationship("BuyerToken", back_populates="buyer")
    packages = relationship("Package", back_populates="buyer")
    allocations = relationship("PackageAllocation", back_populates="buyer")


class BuyerToken(Base):
    """API tokens for buyers"""
    __tablename__ = "buyer_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="tokens")
    
    __table_args__ = (
        Index('idx_token_hash', 'token_hash'),
    )


class Package(Base):
    """Traffic packages for allocation"""
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(255), unique=True, nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip = Column(String(50), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    
    assigned_buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    status = Column(
        String(20), 
        default="available", 
        nullable=False, 
        index=True
    )  # available, allocated, in_progress, completed, failed, revoked
    
    bytes_sent = Column(BigInteger, default=0, nullable=False)
    
    allocated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="packages")
    allocations = relationship("PackageAllocation", back_populates="package")
    
    __table_args__ = (
        Index('idx_status_buyer', 'status', 'assigned_buyer_id'),
        Index('idx_user_ip', 'user_id', 'ip'),
    )


class PackageAllocation(Base):
    """Package allocation history/audit log"""
    __tablename__ = "package_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    
    status = Column(String(20), nullable=False)
    bytes_sent = Column(BigInteger, default=0)
    
    allocated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    package = relationship("Package", back_populates="allocations")
    buyer = relationship("Buyer", back_populates="allocations")
    
    __table_args__ = (
        Index('idx_buyer_status', 'buyer_id', 'status'),
        Index('idx_allocated_at', 'allocated_at'),
    )


class Payment(Base):
    """Payment/withdrawal records"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    method = Column(String(50), default="cryptomus", nullable=False)
    target = Column(String(255), nullable=True)  # Wallet address or email
    
    status = Column(
        String(20), 
        default="pending", 
        nullable=False, 
        index=True
    )  # pending, processing, completed, failed, cancelled
    
    tx_reference = Column(String(255), nullable=True)  # External transaction ID
    tx_hash = Column(String(255), nullable=True)  # Blockchain transaction hash
    
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_status', 'status'),
    )


class Notification(Base):
    """System notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = broadcast
    
    type = Column(String(50), nullable=False)  # login, payment, traffic, system, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    is_read = Column(Boolean, default=False, nullable=False)
    sent_via_bot = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    """Audit trail for important actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    
    user_id = Column(Integer, nullable=True)
    admin_id = Column(Integer, nullable=True)
    buyer_id = Column(Integer, nullable=True)
    
    details = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_action_created', 'action', 'created_at'),
    )


class SystemMetric(Base):
    """System metrics and statistics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    
    tags = Column(Text, nullable=True)  # JSON string for additional metadata
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_metric_timestamp', 'metric_name', 'timestamp'),
    )

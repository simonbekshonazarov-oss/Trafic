"""Database models for the Traffic Share application."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from traffic_share.core.constants import UserStatus, SessionStatus, PackageStatus, PaymentStatus, PaymentMethod

Base = declarative_base()

class User(Base):
    """User model for traffic providers."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    balance = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("TrafficSession", back_populates="user")
    devices = relationship("Device", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Device(Base):
    """Device model for user devices."""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(255), unique=True, index=True, nullable=False)
    os = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    last_active = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="devices")
    sessions = relationship("TrafficSession", back_populates="device")

class LoginCode(Base):
    """Login codes for authentication."""
    __tablename__ = "login_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    code = Column(String(6), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)

class TrafficSession(Base):
    """Traffic sharing sessions."""
    __tablename__ = "traffic_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    bytes_tx = Column(Integer, default=0)
    bytes_rx = Column(Integer, default=0)
    bytes_total = Column(Integer, default=0)
    start_ip = Column(String(45), nullable=True)
    end_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")
    logs = relationship("TrafficLog", back_populates="session")

class TrafficLog(Base):
    """Traffic data logs."""
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("traffic_sessions.id"), nullable=False)
    bytes_tx = Column(Integer, default=0)
    bytes_rx = Column(Integer, default=0)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("TrafficSession", back_populates="logs")

class Buyer(Base):
    """Buyer model for traffic purchasers."""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=True)
    region = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tokens = relationship("BuyerToken", back_populates="buyer")
    allocations = relationship("PackageAllocation", back_populates="buyer")

class BuyerToken(Base):
    """API tokens for buyers."""
    __tablename__ = "buyer_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="tokens")

class Package(Base):
    """Traffic packages for allocation."""
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    status = Column(SQLEnum(PackageStatus), default=PackageStatus.AVAILABLE)
    assigned_buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    bytes_sent = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    buyer = relationship("Buyer")
    allocations = relationship("PackageAllocation", back_populates="package")

class PackageAllocation(Base):
    """Package allocation history."""
    __tablename__ = "package_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    allocated_at = Column(DateTime, default=func.now())
    status = Column(SQLEnum(PackageStatus), nullable=False)
    bytes_sent = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    package = relationship("Package", back_populates="allocations")
    buyer = relationship("Buyer", back_populates="allocations")

class Payment(Base):
    """Payment/withdrawal requests."""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    target = Column(String(255), nullable=False)  # PayPal email, crypto address, etc.
    tx_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")

class Admin(Base):
    """Admin users."""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    is_superadmin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)

class AuditLog(Base):
    """Audit log for system events."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=func.now())

import enum
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class CustomerType(str, enum.Enum):
    company = "company"
    individual = "individual"


class KYCStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    expired = "expired"
    rejected = "rejected"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_type = Column(Enum(CustomerType), nullable=False)
    name = Column(String(300), nullable=False, index=True)
    email = Column(String(254))
    phone = Column(String(50))
    address = Column(Text)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False)
    tax_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contracts = relationship("Contract", back_populates="customer")
    kyc_documents = relationship("KYCDocument", back_populates="customer", cascade="all, delete-orphan")


class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String(100), nullable=False)
    status = Column(Enum(KYCStatus), nullable=False, default=KYCStatus.pending)
    file_reference = Column(String(500))
    expiry_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="kyc_documents")

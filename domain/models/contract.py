import enum
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class LeaseType(str, enum.Enum):
    vehicle = "vehicle"
    equipment = "equipment"
    financial = "financial"


class ContractStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    suspended = "suspended"
    terminated = "terminated"
    expired = "expired"


class PaymentFrequency(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annually = "annually"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    lease_type = Column(Enum(LeaseType), nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.draft)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False)
    asset_description = Column(Text)
    asset_value = Column(Numeric(18, 2))
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    terms = relationship("ContractTerms", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    amendments = relationship("Amendment", back_populates="contract", order_by="Amendment.effective_date")
    customer = relationship("Customer", back_populates="contracts")
    payment_schedule = relationship("PaymentSchedule", back_populates="contract", uselist=False)


class ContractTerms(Base):
    __tablename__ = "contract_terms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, nullable=False)
    duration_months = Column(Numeric(5, 0), nullable=False)
    payment_frequency = Column(Enum(PaymentFrequency), nullable=False, default=PaymentFrequency.monthly)
    interest_rate = Column(Numeric(8, 5), nullable=False)
    residual_value = Column(Numeric(18, 2), default=0)
    down_payment = Column(Numeric(18, 2), default=0)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)

    contract = relationship("Contract", back_populates="terms")


class Amendment(Base):
    __tablename__ = "amendments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    effective_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    changes = Column(Text, nullable=False)  # JSON string of changed fields
    previous_terms_snapshot = Column(Text)  # JSON snapshot of terms before amendment
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("Contract", back_populates="amendments")


class ContractTemplate(Base):
    __tablename__ = "contract_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False)
    lease_type = Column(Enum(LeaseType), nullable=False)
    name = Column(String(200), nullable=False)
    template_config = Column(Text, nullable=False)  # JSON config
    created_at = Column(DateTime(timezone=True), server_default=func.now())

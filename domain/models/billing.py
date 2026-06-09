import enum
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class InstallmentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_installments = Column(Integer, nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("Contract", back_populates="payment_schedule")
    installments = relationship("Installment", back_populates="schedule", order_by="Installment.due_date", cascade="all, delete-orphan")


class Installment(Base):
    __tablename__ = "installments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("payment_schedules.id", ondelete="CASCADE"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    principal = Column(Numeric(18, 2), nullable=False)
    interest = Column(Numeric(18, 2), nullable=False)
    status = Column(Enum(InstallmentStatus), nullable=False, default=InstallmentStatus.pending)
    paid_date = Column(Date)

    schedule = relationship("PaymentSchedule", back_populates="installments")

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class TaxType(str, enum.Enum):
    vat = "vat"
    withholding = "withholding"
    stamp_duty = "stamp_duty"


class Country(Base):
    __tablename__ = "countries"

    code = Column(String(3), primary_key=True)
    name = Column(String(200), nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    locale = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Currency(Base):
    __tablename__ = "currencies"

    code = Column(String(3), primary_key=True)
    name = Column(String(100), nullable=False)
    exchange_rate_to_usd = Column(Numeric(18, 8), nullable=False, default=1.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TaxRule(Base):
    __tablename__ = "tax_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    country_code = Column(String(3), ForeignKey("countries.code"), nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False)
    rate = Column(Numeric(8, 5), nullable=False)
    description = Column(String(300))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

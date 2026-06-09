"""Configuration domain models: Country, Currency, TaxRule."""

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TaxType(str, enum.Enum):
    VAT = "vat"
    WITHHOLDING = "withholding"
    STAMP_DUTY = "stamp_duty"
    INCOME_TAX = "income_tax"


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(10), default="")
    exchange_rate_to_usd: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal("1.0")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    countries: Mapped[list["Country"]] = relationship(back_populates="currency")


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code")
    )
    locale: Mapped[str] = mapped_column(String(10), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    currency: Mapped["Currency"] = relationship(back_populates="countries")
    tax_rules: Mapped[list["TaxRule"]] = relationship(back_populates="country")


class TaxRule(Base):
    __tablename__ = "tax_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(
        String(2), ForeignKey("countries.code")
    )
    tax_type: Mapped[TaxType] = mapped_column(Enum(TaxType))
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    name: Mapped[str] = mapped_column(String(100))
    applicable_to: Mapped[str] = mapped_column(String(50), default="all")
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    country: Mapped["Country"] = relationship(back_populates="tax_rules")

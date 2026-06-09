"""Pydantic schemas for Configuration context (Country, Currency, TaxRule)."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from domain.models.configuration import TaxType


# --- Currency ---
class CurrencyBase(BaseModel):
    code: str = Field(max_length=3)
    name: str = Field(max_length=100)
    symbol: str = Field(default="", max_length=10)
    exchange_rate_to_usd: Decimal = Field(default=Decimal("1.0"), ge=0)
    is_active: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyRead(CurrencyBase):
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CurrencyUpdate(BaseModel):
    name: str | None = None
    symbol: str | None = None
    exchange_rate_to_usd: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


# --- TaxRule ---
class TaxRuleBase(BaseModel):
    tax_type: TaxType
    rate: Decimal = Field(ge=0, le=1)
    name: str = Field(max_length=100)
    applicable_to: str = Field(default="all", max_length=50)
    effective_from: date
    effective_to: date | None = None


class TaxRuleCreate(TaxRuleBase):
    country_code: str = Field(max_length=2)


class TaxRuleRead(TaxRuleBase):
    id: int
    country_code: str

    model_config = {"from_attributes": True}


# --- Country ---
class CountryBase(BaseModel):
    code: str = Field(max_length=2)
    name: str = Field(max_length=100)
    currency_code: str = Field(max_length=3)
    locale: str = Field(default="en", max_length=10)
    is_active: bool = True


class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CountryConfigRead(CountryRead):
    """Country with nested currency and tax rules."""

    currency: CurrencyRead | None = None
    tax_rules: list[TaxRuleRead] = []

    model_config = {"from_attributes": True}

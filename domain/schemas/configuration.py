from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.configuration import TaxType


class CountryCreate(BaseModel):
    code: str
    name: str
    currency_code: str
    locale: str = "en"


class CountryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    currency_code: str
    locale: str
    created_at: datetime


class CurrencyCreate(BaseModel):
    code: str
    name: str
    exchange_rate_to_usd: Decimal = Decimal("1.0")


class CurrencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    exchange_rate_to_usd: Decimal
    updated_at: datetime


class TaxRuleCreate(BaseModel):
    country_code: str
    tax_type: TaxType
    rate: Decimal
    description: str | None = None


class TaxRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    country_code: str
    tax_type: TaxType
    rate: Decimal
    description: str | None
    created_at: datetime

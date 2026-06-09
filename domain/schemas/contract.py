from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.contract import ContractStatus, LeaseType, PaymentFrequency


class ContractTermsCreate(BaseModel):
    duration_months: int
    payment_frequency: PaymentFrequency = PaymentFrequency.monthly
    interest_rate: Decimal
    residual_value: Decimal = Decimal("0")
    down_payment: Decimal = Decimal("0")
    currency_code: str


class ContractTermsRead(ContractTermsCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class ContractCreate(BaseModel):
    contract_number: str
    lease_type: LeaseType
    customer_id: UUID
    country_code: str
    asset_description: str | None = None
    asset_value: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    terms: ContractTermsCreate | None = None


class ContractUpdate(BaseModel):
    asset_description: str | None = None
    asset_value: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    contract_number: str
    lease_type: LeaseType
    status: ContractStatus
    customer_id: UUID
    country_code: str
    asset_description: str | None
    asset_value: Decimal | None
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime
    terms: ContractTermsRead | None = None


class AmendmentCreate(BaseModel):
    effective_date: date
    reason: str
    changes: str


class AmendmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    contract_id: UUID
    effective_date: date
    reason: str
    changes: str
    previous_terms_snapshot: str | None
    created_at: datetime


class ContractTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    country_code: str
    lease_type: LeaseType
    name: str
    template_config: str
    created_at: datetime

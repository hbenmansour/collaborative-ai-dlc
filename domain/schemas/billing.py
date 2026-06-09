from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.billing import InstallmentStatus


class InstallmentCreate(BaseModel):
    installment_number: int
    due_date: date
    amount: Decimal
    principal: Decimal
    interest: Decimal


class InstallmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    installment_number: int
    due_date: date
    amount: Decimal
    principal: Decimal
    interest: Decimal
    status: InstallmentStatus
    paid_date: date | None


class PaymentScheduleCreate(BaseModel):
    contract_id: UUID
    total_installments: int
    currency_code: str
    installments: list[InstallmentCreate]


class PaymentScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    contract_id: UUID
    total_installments: int
    currency_code: str
    created_at: datetime
    installments: list[InstallmentRead] = []

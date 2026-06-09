from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.customer import CustomerType, KYCStatus


class CustomerCreate(BaseModel):
    customer_type: CustomerType
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    country_code: str
    tax_id: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    customer_type: CustomerType
    name: str
    email: str | None
    phone: str | None
    address: str | None
    country_code: str
    tax_id: str | None
    created_at: datetime
    updated_at: datetime


class KYCDocumentCreate(BaseModel):
    doc_type: str
    file_reference: str | None = None
    expiry_date: date | None = None


class KYCDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    customer_id: UUID
    doc_type: str
    status: KYCStatus
    file_reference: str | None
    expiry_date: date | None
    created_at: datetime

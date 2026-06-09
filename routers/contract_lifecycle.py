"""Contract lifecycle API endpoints - thin layer for state transitions.

Endpoints: activate, amend, renew, terminate.
Business rules live in agent skills; this layer validates and persists.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.schemas.contract import ContractRead
from middleware.auth import CurrentUser
from middleware.rbac import require_permissions
from services.contract_lifecycle_service import ContractLifecycleService

router = APIRouter(prefix="/contracts", tags=["contract-lifecycle"])


class ActivateRequest(BaseModel):
    activation_date: date | None = Field(None, description="Activation date; defaults to today")


class AmendRequest(BaseModel):
    effective_date: date
    reason: str
    changes: dict = Field(..., description="Fields to change on contract terms")


class RenewRequest(BaseModel):
    new_end_date: date
    new_terms: dict | None = Field(None, description="Optional updated terms")


class TerminateRequest(BaseModel):
    termination_date: date
    reason: str


@router.post("/{contract_id}/activate", response_model=ContractRead)
async def activate_contract(
    contract_id: UUID,
    body: ActivateRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:update")),
):
    """Activate a draft contract."""
    service = ContractLifecycleService(db)
    return await service.activate(contract_id, body.activation_date)


@router.post("/{contract_id}/amend", response_model=ContractRead)
async def amend_contract(
    contract_id: UUID,
    body: AmendRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:update")),
):
    """Create an amendment on an active contract."""
    service = ContractLifecycleService(db)
    return await service.amend(contract_id, body.effective_date, body.reason, body.changes)


@router.post("/{contract_id}/renew", response_model=ContractRead)
async def renew_contract(
    contract_id: UUID,
    body: RenewRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:update")),
):
    """Renew an active or expired contract."""
    service = ContractLifecycleService(db)
    return await service.renew(contract_id, body.new_end_date, body.new_terms)


@router.post("/{contract_id}/terminate", response_model=ContractRead)
async def terminate_contract(
    contract_id: UUID,
    body: TerminateRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:update")),
):
    """Terminate an active contract early."""
    service = ContractLifecycleService(db)
    return await service.terminate(contract_id, body.termination_date, body.reason)

"""Billing API endpoints - payment schedule persistence and retrieval."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.schemas.billing import PaymentScheduleCreate, PaymentScheduleRead
from middleware.auth import CurrentUser
from middleware.rbac import require_permissions
from services.payment_schedule_service import PaymentScheduleService

router = APIRouter(prefix="/contracts", tags=["billing"])


@router.post(
    "/{contract_id}/schedule/generate",
    response_model=PaymentScheduleRead,
    status_code=201,
)
async def generate_schedule(
    contract_id: UUID,
    data: PaymentScheduleCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("billing:create")),
):
    """Persist a computed payment schedule for a contract."""
    service = PaymentScheduleService(db)
    return await service.generate_schedule(contract_id, data)


@router.get("/{contract_id}/schedule", response_model=PaymentScheduleRead)
async def get_schedule(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("billing:read")),
):
    """Retrieve the payment schedule for a contract."""
    service = PaymentScheduleService(db)
    return await service.get_schedule(contract_id)

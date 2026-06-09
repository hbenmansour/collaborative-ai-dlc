"""Contract CRUD API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.models.contract import ContractStatus, LeaseType
from domain.schemas.contract import ContractCreate, ContractRead, ContractUpdate
from middleware.auth import CurrentUser
from middleware.rbac import require_permissions
from services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])


class PaginatedContracts(BaseModel):
    items: list[ContractRead]
    total: int
    offset: int
    limit: int


@router.post("", response_model=ContractRead, status_code=201)
async def create_contract(
    data: ContractCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:create")),
):
    """Create a new draft contract."""
    service = ContractService(db)
    return await service.create_contract(data)


@router.get("", response_model=PaginatedContracts)
async def list_contracts(
    status: ContractStatus | None = Query(None),
    lease_type: LeaseType | None = Query(None),
    customer_id: UUID | None = Query(None),
    country_code: str | None = Query(None),
    search: str | None = Query(None, description="Search contract number or asset description"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:read")),
):
    """List contracts with filtering, search, and pagination."""
    service = ContractService(db)
    items, total = await service.list_contracts(
        status_filter=status,
        lease_type=lease_type,
        customer_id=customer_id,
        country_code=country_code,
        search=search,
        offset=offset,
        limit=limit,
    )
    return PaginatedContracts(items=items, total=total, offset=offset, limit=limit)


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:read")),
):
    """Get contract detail by ID."""
    service = ContractService(db)
    return await service.get_contract(contract_id)


@router.put("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: UUID,
    data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permissions("contract:update")),
):
    """Update a draft contract."""
    service = ContractService(db)
    return await service.update_contract(contract_id, data)

"""Contract service - business validation and orchestration for contract CRUD."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.contract import Contract, ContractStatus, ContractTerms, LeaseType
from domain.schemas.contract import ContractCreate, ContractUpdate
from repositories.contract_repository import ContractRepository


class ContractService:
    def __init__(self, db: AsyncSession):
        self.repo = ContractRepository(db)

    async def create_contract(self, data: ContractCreate) -> Contract:
        contract = Contract(
            contract_number=data.contract_number,
            lease_type=data.lease_type,
            status=ContractStatus.draft,
            customer_id=data.customer_id,
            country_code=data.country_code,
            asset_description=data.asset_description,
            asset_value=data.asset_value,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        if data.terms:
            contract.terms = ContractTerms(
                duration_months=data.terms.duration_months,
                payment_frequency=data.terms.payment_frequency,
                interest_rate=data.terms.interest_rate,
                residual_value=data.terms.residual_value,
                down_payment=data.terms.down_payment,
                currency_code=data.terms.currency_code,
            )
        return await self.repo.create(contract)

    async def get_contract(self, contract_id: UUID) -> Contract:
        contract = await self.repo.get_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found",
            )
        return contract

    async def list_contracts(
        self,
        *,
        status_filter: ContractStatus | None = None,
        lease_type: LeaseType | None = None,
        customer_id: UUID | None = None,
        country_code: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Contract], int]:
        return await self.repo.list(
            status=status_filter,
            lease_type=lease_type,
            customer_id=customer_id,
            country_code=country_code,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def update_contract(self, contract_id: UUID, data: ContractUpdate) -> Contract:
        contract = await self.get_contract(contract_id)
        if contract.status != ContractStatus.draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft contracts can be updated",
            )
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contract, field, value)
        return await self.repo.update(contract)

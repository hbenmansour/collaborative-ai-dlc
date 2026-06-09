"""Contract repository - data access layer for contracts."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.models.contract import Contract, ContractStatus, ContractTerms, LeaseType


class ContractRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, contract: Contract) -> Contract:
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract, attribute_names=["terms"])
        return contract

    async def get_by_id(self, contract_id: UUID) -> Contract | None:
        stmt = (
            select(Contract)
            .options(selectinload(Contract.terms))
            .where(Contract.id == contract_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        status: ContractStatus | None = None,
        lease_type: LeaseType | None = None,
        customer_id: UUID | None = None,
        country_code: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Contract], int]:
        stmt = select(Contract).options(selectinload(Contract.terms))
        count_stmt = select(func.count(Contract.id))

        if status:
            stmt = stmt.where(Contract.status == status)
            count_stmt = count_stmt.where(Contract.status == status)
        if lease_type:
            stmt = stmt.where(Contract.lease_type == lease_type)
            count_stmt = count_stmt.where(Contract.lease_type == lease_type)
        if customer_id:
            stmt = stmt.where(Contract.customer_id == customer_id)
            count_stmt = count_stmt.where(Contract.customer_id == customer_id)
        if country_code:
            stmt = stmt.where(Contract.country_code == country_code)
            count_stmt = count_stmt.where(Contract.country_code == country_code)
        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                Contract.contract_number.ilike(pattern),
                Contract.asset_description.ilike(pattern),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Contract.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def update(self, contract: Contract) -> Contract:
        await self.db.commit()
        await self.db.refresh(contract, attribute_names=["terms"])
        return contract

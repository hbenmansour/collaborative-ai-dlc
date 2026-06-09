"""Payment schedule repository - data access layer for payment schedules."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.models.billing import Installment, PaymentSchedule


class ScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_contract_id(self, contract_id: UUID) -> PaymentSchedule | None:
        stmt = (
            select(PaymentSchedule)
            .options(selectinload(PaymentSchedule.installments))
            .where(PaymentSchedule.contract_id == contract_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_contract_id(self, contract_id: UUID) -> None:
        existing = await self.get_by_contract_id(contract_id)
        if existing:
            await self.db.delete(existing)
            await self.db.flush()

    async def create(self, schedule: PaymentSchedule) -> PaymentSchedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule, attribute_names=["installments"])
        return schedule

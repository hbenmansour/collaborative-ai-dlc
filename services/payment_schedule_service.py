"""Payment schedule service - validates and persists computed schedules."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.billing import Installment, PaymentSchedule
from domain.models.contract import Contract, ContractStatus
from domain.schemas.billing import PaymentScheduleCreate
from repositories.contract_repository import ContractRepository
from repositories.schedule_repository import ScheduleRepository


class PaymentScheduleService:
    def __init__(self, db: AsyncSession):
        self.repo = ScheduleRepository(db)
        self.contract_repo = ContractRepository(db)

    async def generate_schedule(self, contract_id: UUID, data: PaymentScheduleCreate) -> PaymentSchedule:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found",
            )
        if contract.status not in (ContractStatus.draft, ContractStatus.active):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment schedules can only be generated for draft or active contracts",
            )

        # Replace existing schedule if present (re-generation on amendment)
        await self.repo.delete_by_contract_id(contract_id)

        schedule = PaymentSchedule(
            contract_id=contract_id,
            total_installments=data.total_installments,
            currency_code=data.currency_code,
        )
        schedule.installments = [
            Installment(
                installment_number=inst.installment_number,
                due_date=inst.due_date,
                amount=inst.amount,
                principal=inst.principal,
                interest=inst.interest,
            )
            for inst in data.installments
        ]
        return await self.repo.create(schedule)

    async def get_schedule(self, contract_id: UUID) -> PaymentSchedule:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found",
            )
        schedule = await self.repo.get_by_contract_id(contract_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payment schedule found for contract {contract_id}",
            )
        return schedule

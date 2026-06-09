"""Contract lifecycle service - thin validation + persistence layer.

Complex business rules (penalty calculation, amortization, state transition decisions)
live in agent skills. This service only validates required fields, checks status
preconditions, and persists state changes.
"""

import json
from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.contract import Amendment, Contract, ContractStatus, ContractTerms
from repositories.contract_repository import ContractRepository


class ContractLifecycleService:
    def __init__(self, db: AsyncSession):
        self.repo = ContractRepository(db)
        self.db = db

    async def _get_contract(self, contract_id: UUID) -> Contract:
        contract = await self.repo.get_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found",
            )
        return contract

    async def activate(self, contract_id: UUID, activation_date: date | None = None) -> Contract:
        """Activate a draft contract. Validates status is 'draft'."""
        contract = await self._get_contract(contract_id)
        if contract.status != ContractStatus.draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only draft contracts can be activated. Current status: {contract.status.value}",
            )
        if not contract.terms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract must have terms defined before activation",
            )
        contract.status = ContractStatus.active
        contract.start_date = activation_date or date.today()
        return await self.repo.update(contract)

    async def amend(
        self,
        contract_id: UUID,
        effective_date: date,
        reason: str,
        changes: dict,
    ) -> Contract:
        """Amend an active contract. Persists amendment record and applies changes."""
        contract = await self._get_contract(contract_id)
        if contract.status != ContractStatus.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only active contracts can be amended. Current status: {contract.status.value}",
            )
        # Snapshot current terms
        previous_snapshot = None
        if contract.terms:
            previous_snapshot = json.dumps({
                "duration_months": int(contract.terms.duration_months),
                "payment_frequency": contract.terms.payment_frequency.value,
                "interest_rate": str(contract.terms.interest_rate),
                "residual_value": str(contract.terms.residual_value),
                "down_payment": str(contract.terms.down_payment),
                "currency_code": contract.terms.currency_code,
            })

        amendment = Amendment(
            contract_id=contract_id,
            effective_date=effective_date,
            reason=reason,
            changes=json.dumps(changes),
            previous_terms_snapshot=previous_snapshot,
        )
        self.db.add(amendment)

        # Apply term changes if provided
        if contract.terms and changes:
            for field, value in changes.items():
                if hasattr(contract.terms, field):
                    setattr(contract.terms, field, value)

        await self.db.commit()
        await self.db.refresh(contract, attribute_names=["terms", "amendments"])
        return contract

    async def renew(
        self,
        contract_id: UUID,
        new_end_date: date,
        new_terms: dict | None = None,
    ) -> Contract:
        """Renew an active or expiring contract with new end date."""
        contract = await self._get_contract(contract_id)
        if contract.status not in (ContractStatus.active, ContractStatus.expired):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only active or expired contracts can be renewed. Current status: {contract.status.value}",
            )
        contract.end_date = new_end_date
        contract.status = ContractStatus.active

        if contract.terms and new_terms:
            for field, value in new_terms.items():
                if hasattr(contract.terms, field):
                    setattr(contract.terms, field, value)

        return await self.repo.update(contract)

    async def terminate(
        self,
        contract_id: UUID,
        termination_date: date,
        reason: str,
    ) -> Contract:
        """Terminate an active contract early."""
        contract = await self._get_contract(contract_id)
        if contract.status != ContractStatus.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only active contracts can be terminated. Current status: {contract.status.value}",
            )
        contract.status = ContractStatus.terminated
        contract.end_date = termination_date
        return await self.repo.update(contract)

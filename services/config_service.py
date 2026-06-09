"""Service layer for Configuration context."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.configuration import Country, Currency, TaxRule
from domain.schemas.configuration import (
    CountryCreate,
    CurrencyCreate,
    CurrencyUpdate,
    TaxRuleCreate,
)
from repositories.config_repository import ConfigRepository


class ConfigService:
    def __init__(self, db: AsyncSession):
        self.repo = ConfigRepository(db)
        self.db = db

    # --- Currency ---
    async def list_currencies(self, active_only: bool = True) -> list[Currency]:
        return await self.repo.list_currencies(active_only)

    async def get_currency(self, code: str) -> Currency:
        currency = await self.repo.get_currency(code)
        if not currency:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Currency '{code}' not found")
        return currency

    async def create_currency(self, data: CurrencyCreate) -> Currency:
        existing = await self.repo.get_currency(data.code)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Currency '{data.code}' already exists")
        currency = Currency(**data.model_dump())
        await self.repo.create_currency(currency)
        await self.db.commit()
        return currency

    async def update_currency(self, code: str, data: CurrencyUpdate) -> Currency:
        currency = await self.get_currency(code)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(currency, field, value)
        await self.repo.update_currency(currency)
        await self.db.commit()
        return currency

    # --- Country ---
    async def list_countries(self, active_only: bool = True) -> list[Country]:
        return await self.repo.list_countries(active_only)

    async def get_country_config(self, code: str) -> Country:
        country = await self.repo.get_country_config(code)
        if not country:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Country '{code}' not found")
        return country

    async def create_country(self, data: CountryCreate) -> Country:
        existing = await self.repo.get_country(data.code)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Country '{data.code}' already exists")
        # Validate currency exists
        currency = await self.repo.get_currency(data.currency_code)
        if not currency:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Currency '{data.currency_code}' does not exist",
            )
        country = Country(**data.model_dump())
        await self.repo.create_country(country)
        await self.db.commit()
        return country

    # --- TaxRule ---
    async def list_tax_rules(self, country_code: str) -> list[TaxRule]:
        # Validate country exists
        country = await self.repo.get_country(country_code)
        if not country:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Country '{country_code}' not found")
        return await self.repo.list_tax_rules(country_code)

    async def create_tax_rule(self, data: TaxRuleCreate) -> TaxRule:
        country = await self.repo.get_country(data.country_code)
        if not country:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Country '{data.country_code}' does not exist",
            )
        tax_rule = TaxRule(**data.model_dump())
        await self.repo.create_tax_rule(tax_rule)
        await self.db.commit()
        return tax_rule

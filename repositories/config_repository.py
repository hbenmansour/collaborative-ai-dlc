"""Repository layer for Configuration context."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.models.configuration import Country, Currency, TaxRule


class ConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Currency ---
    async def list_currencies(self, active_only: bool = True) -> list[Currency]:
        stmt = select(Currency)
        if active_only:
            stmt = stmt.where(Currency.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_currency(self, code: str) -> Currency | None:
        return await self.db.get(Currency, code)

    async def create_currency(self, currency: Currency) -> Currency:
        self.db.add(currency)
        await self.db.flush()
        return currency

    async def update_currency(self, currency: Currency) -> Currency:
        await self.db.flush()
        return currency

    # --- Country ---
    async def list_countries(self, active_only: bool = True) -> list[Country]:
        stmt = select(Country)
        if active_only:
            stmt = stmt.where(Country.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_country(self, code: str) -> Country | None:
        return await self.db.get(Country, code)

    async def get_country_config(self, code: str) -> Country | None:
        stmt = (
            select(Country)
            .options(selectinload(Country.currency), selectinload(Country.tax_rules))
            .where(Country.code == code)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_country(self, country: Country) -> Country:
        self.db.add(country)
        await self.db.flush()
        return country

    # --- TaxRule ---
    async def list_tax_rules(self, country_code: str) -> list[TaxRule]:
        stmt = select(TaxRule).where(TaxRule.country_code == country_code)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_tax_rule(self, tax_rule: TaxRule) -> TaxRule:
        self.db.add(tax_rule)
        await self.db.flush()
        return tax_rule

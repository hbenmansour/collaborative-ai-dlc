"""Seed data for initial country configuration."""

import asyncio
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from database import async_session
from domain.models.configuration import Country, Currency, TaxRule, TaxType

CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "symbol": "$", "exchange_rate_to_usd": Decimal("1.0")},
    {"code": "EUR", "name": "Euro", "symbol": "€", "exchange_rate_to_usd": Decimal("1.08")},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "exchange_rate_to_usd": Decimal("1.27")},
    {"code": "MAD", "name": "Moroccan Dirham", "symbol": "د.م.", "exchange_rate_to_usd": Decimal("0.10")},
    {"code": "XOF", "name": "CFA Franc", "symbol": "CFA", "exchange_rate_to_usd": Decimal("0.0016")},
]

COUNTRIES = [
    {"code": "US", "name": "United States", "currency_code": "USD", "locale": "en"},
    {"code": "FR", "name": "France", "currency_code": "EUR", "locale": "fr"},
    {"code": "GB", "name": "United Kingdom", "currency_code": "GBP", "locale": "en"},
    {"code": "MA", "name": "Morocco", "currency_code": "MAD", "locale": "fr"},
    {"code": "SN", "name": "Senegal", "currency_code": "XOF", "locale": "fr"},
]

TAX_RULES = [
    {"country_code": "FR", "tax_type": TaxType.VAT, "rate": Decimal("0.2000"), "name": "TVA Standard", "applicable_to": "all", "effective_from": date(2024, 1, 1)},
    {"country_code": "FR", "tax_type": TaxType.WITHHOLDING, "rate": Decimal("0.2500"), "name": "Prélèvement à la source", "applicable_to": "income", "effective_from": date(2024, 1, 1)},
    {"country_code": "GB", "tax_type": TaxType.VAT, "rate": Decimal("0.2000"), "name": "UK VAT Standard", "applicable_to": "all", "effective_from": date(2024, 1, 1)},
    {"country_code": "MA", "tax_type": TaxType.VAT, "rate": Decimal("0.2000"), "name": "TVA Maroc", "applicable_to": "all", "effective_from": date(2024, 1, 1)},
    {"country_code": "MA", "tax_type": TaxType.WITHHOLDING, "rate": Decimal("0.1500"), "name": "Retenue à la source", "applicable_to": "services", "effective_from": date(2024, 1, 1)},
    {"country_code": "SN", "tax_type": TaxType.VAT, "rate": Decimal("0.1800"), "name": "TVA Sénégal", "applicable_to": "all", "effective_from": date(2024, 1, 1)},
]


async def seed_configuration():
    """Insert seed data if tables are empty."""
    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(Currency).limit(1))
        if result.scalar_one_or_none():
            print("Configuration already seeded, skipping.")
            return

        for c in CURRENCIES:
            db.add(Currency(**c))
        await db.flush()

        for c in COUNTRIES:
            db.add(Country(**c))
        await db.flush()

        for t in TAX_RULES:
            db.add(TaxRule(**t))

        await db.commit()
        print(f"Seeded {len(CURRENCIES)} currencies, {len(COUNTRIES)} countries, {len(TAX_RULES)} tax rules.")


if __name__ == "__main__":
    asyncio.run(seed_configuration())

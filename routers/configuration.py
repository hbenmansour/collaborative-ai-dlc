"""Configuration API endpoints: countries, currencies, tax rules."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.schemas.configuration import (
    CountryConfigRead,
    CountryCreate,
    CountryRead,
    CurrencyCreate,
    CurrencyRead,
    CurrencyUpdate,
    TaxRuleCreate,
    TaxRuleRead,
)
from middleware.auth import CurrentUser, get_current_user
from services.config_service import ConfigService

router = APIRouter(prefix="/api/v1", tags=["configuration"])


def _service(db: AsyncSession = Depends(get_db)) -> ConfigService:
    return ConfigService(db)


# --- Currencies ---
@router.get("/currencies", response_model=list[CurrencyRead])
async def list_currencies(
    active_only: bool = Query(True),
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """List all currencies with exchange rates."""
    return await service.list_currencies(active_only)


@router.post("/currencies", response_model=CurrencyRead, status_code=201)
async def create_currency(
    data: CurrencyCreate,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Create a new currency."""
    return await service.create_currency(data)


@router.patch("/currencies/{code}", response_model=CurrencyRead)
async def update_currency(
    code: str,
    data: CurrencyUpdate,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Update currency (e.g. exchange rate)."""
    return await service.update_currency(code, data)


# --- Countries ---
@router.get("/countries", response_model=list[CountryRead])
async def list_countries(
    active_only: bool = Query(True),
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """List all configured countries."""
    return await service.list_countries(active_only)


@router.post("/countries", response_model=CountryRead, status_code=201)
async def create_country(
    data: CountryCreate,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Create a new country entity."""
    return await service.create_country(data)


@router.get("/countries/{code}/config", response_model=CountryConfigRead)
async def get_country_config(
    code: str,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Get full country configuration with currency and tax rules."""
    return await service.get_country_config(code)


# --- Tax Rules ---
@router.get("/countries/{country_code}/tax-rules", response_model=list[TaxRuleRead])
async def list_tax_rules(
    country_code: str,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """List tax rules for a country."""
    return await service.list_tax_rules(country_code)


@router.post("/countries/{country_code}/tax-rules", response_model=TaxRuleRead, status_code=201)
async def create_tax_rule(
    country_code: str,
    data: TaxRuleCreate,
    service: ConfigService = Depends(_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Create a tax rule for a country."""
    data.country_code = country_code
    return await service.create_tax_rule(data)

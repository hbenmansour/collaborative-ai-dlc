"""RBAC decorator and country-level access control for FastAPI endpoints."""

from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, status

from config.roles import ROLES, Role
from middleware.auth import CurrentUser, get_current_user


def require_permissions(*permissions: str):
    """Dependency factory: ensures the current user has ALL specified permissions.

    Usage:
        @router.get("/contracts")
        async def list_contracts(user: CurrentUser = Depends(require_permissions("contract:read"))):
            ...
    """

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        user_permissions: set[str] = set()
        for role_name in user.roles:
            try:
                role = Role(role_name)
            except ValueError:
                continue
            user_permissions.update(ROLES.get(role, set()))

        missing = set(permissions) - user_permissions
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(sorted(missing))}",
            )
        return user

    return _check


def require_roles(*roles: str):
    """Dependency factory: ensures the current user has at least one of the specified roles.

    Usage:
        @router.post("/admin/users")
        async def create_user(user: CurrentUser = Depends(require_roles("admin"))):
            ...
    """

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(r in roles for r in user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(roles)}",
            )
        return user

    return _check


def require_country_access(country_code_param: str = "country_code"):
    """Dependency factory: ensures the user has access to the specified country.

    Extracts the country code from path parameters and checks against
    the user's allowed countries. Admin role bypasses country checks.

    Usage:
        @router.get("/countries/{country_code}/contracts")
        async def list_by_country(
            country_code: str,
            user: CurrentUser = Depends(require_country_access("country_code")),
        ):
            ...
    """

    from fastapi import Request

    async def _check(request: Request, user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        # Admin bypasses country restriction
        if Role.ADMIN.value in user.roles:
            return user

        country_code = request.path_params.get(country_code_param)
        if country_code and user.countries and country_code not in user.countries:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to country: {country_code}",
            )
        return user

    return _check

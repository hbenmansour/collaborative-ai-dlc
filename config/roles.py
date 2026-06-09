"""Predefined roles and permissions for the Leasing ERP RBAC system."""

from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    BACK_OFFICE = "back-office"
    FINANCE = "finance"
    MANAGER = "manager"
    AUDITOR = "auditor"


class Permission(str, Enum):
    # Contract permissions
    CONTRACT_CREATE = "contract:create"
    CONTRACT_READ = "contract:read"
    CONTRACT_UPDATE = "contract:update"
    CONTRACT_DELETE = "contract:delete"
    CONTRACT_ACTIVATE = "contract:activate"
    CONTRACT_AMEND = "contract:amend"
    CONTRACT_RENEW = "contract:renew"
    CONTRACT_TERMINATE = "contract:terminate"

    # Customer permissions
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_READ = "customer:read"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_DELETE = "customer:delete"

    # Billing permissions
    BILLING_CREATE = "billing:create"
    BILLING_READ = "billing:read"
    BILLING_UPDATE = "billing:update"

    # Configuration permissions
    CONFIG_CREATE = "config:create"
    CONFIG_READ = "config:read"
    CONFIG_UPDATE = "config:update"
    CONFIG_DELETE = "config:delete"

    # Reporting permissions
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"

    # Admin permissions
    USER_MANAGE = "user:manage"


# Role-permission matrix
ROLES: dict[Role, set[str]] = {
    Role.ADMIN: {p.value for p in Permission},  # All permissions
    Role.BACK_OFFICE: {
        Permission.CONTRACT_CREATE.value,
        Permission.CONTRACT_READ.value,
        Permission.CONTRACT_UPDATE.value,
        Permission.CONTRACT_ACTIVATE.value,
        Permission.CONTRACT_AMEND.value,
        Permission.CONTRACT_RENEW.value,
        Permission.CONTRACT_TERMINATE.value,
        Permission.CUSTOMER_CREATE.value,
        Permission.CUSTOMER_READ.value,
        Permission.CUSTOMER_UPDATE.value,
        Permission.BILLING_CREATE.value,
        Permission.BILLING_READ.value,
        Permission.CONFIG_READ.value,
        Permission.REPORT_READ.value,
    },
    Role.FINANCE: {
        Permission.CONTRACT_READ.value,
        Permission.CUSTOMER_READ.value,
        Permission.BILLING_CREATE.value,
        Permission.BILLING_READ.value,
        Permission.BILLING_UPDATE.value,
        Permission.CONFIG_READ.value,
        Permission.REPORT_READ.value,
        Permission.REPORT_EXPORT.value,
    },
    Role.MANAGER: {
        Permission.CONTRACT_READ.value,
        Permission.CONTRACT_ACTIVATE.value,
        Permission.CONTRACT_TERMINATE.value,
        Permission.CUSTOMER_READ.value,
        Permission.BILLING_READ.value,
        Permission.CONFIG_READ.value,
        Permission.REPORT_READ.value,
        Permission.REPORT_EXPORT.value,
    },
    Role.AUDITOR: {
        Permission.CONTRACT_READ.value,
        Permission.CUSTOMER_READ.value,
        Permission.BILLING_READ.value,
        Permission.CONFIG_READ.value,
        Permission.REPORT_READ.value,
        Permission.REPORT_EXPORT.value,
    },
}

# Convenience lookup: permission string -> set of roles that have it
PERMISSIONS: dict[str, set[Role]] = {}
for role, perms in ROLES.items():
    for perm in perms:
        PERMISSIONS.setdefault(perm, set()).add(role)

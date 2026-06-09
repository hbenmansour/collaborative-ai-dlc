"""Domain API tool for Bedrock AgentCore.

Provides REST client operations for the Leasing ERP Domain API,
enabling the agent to perform CRUD on domain objects.
"""

import json
import os
from typing import Any

import httpx

DOMAIN_API_BASE_URL = os.environ.get("DOMAIN_API_BASE_URL", "http://localhost:8000")

TOOL_SPEC = {
    "name": "domain-api",
    "description": (
        "REST client for the Leasing ERP Domain API. "
        "Performs CRUD operations on contracts, customers, payments, and configuration."
    ),
    "actions": [
        {
            "name": "create_contract",
            "description": "Create a new draft lease contract",
            "parameters": {
                "type": "object",
                "properties": {
                    "lease_type": {"type": "string", "enum": ["vehicle", "equipment", "financial"]},
                    "customer_id": {"type": "string"},
                    "country_code": {"type": "string"},
                    "asset_description": {"type": "string"},
                    "duration_months": {"type": "integer"},
                    "payment_frequency": {"type": "string", "enum": ["monthly", "quarterly", "annually"]},
                    "interest_rate": {"type": "number"},
                    "residual_value": {"type": "number"},
                    "down_payment": {"type": "number"},
                    "asset_value": {"type": "number"},
                },
                "required": ["lease_type", "customer_id", "country_code", "asset_value", "duration_months"],
            },
        },
        {
            "name": "get_contract",
            "description": "Retrieve a contract by ID",
            "parameters": {
                "type": "object",
                "properties": {"contract_id": {"type": "string"}},
                "required": ["contract_id"],
            },
        },
        {
            "name": "list_contracts",
            "description": "List contracts with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["draft", "active", "suspended", "terminated", "expired"]},
                    "lease_type": {"type": "string"},
                    "customer_id": {"type": "string"},
                    "country_code": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 20},
                },
            },
        },
        {
            "name": "update_contract",
            "description": "Update a draft contract's fields",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string"},
                    "updates": {"type": "object"},
                },
                "required": ["contract_id", "updates"],
            },
        },
        {
            "name": "activate_contract",
            "description": "Activate a draft contract (triggers billing schedule generation)",
            "parameters": {
                "type": "object",
                "properties": {"contract_id": {"type": "string"}},
                "required": ["contract_id"],
            },
        },
        {
            "name": "amend_contract",
            "description": "Create an amendment on an active contract",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string"},
                    "effective_date": {"type": "string", "format": "date"},
                    "changes": {"type": "object"},
                    "reason": {"type": "string"},
                },
                "required": ["contract_id", "effective_date", "changes", "reason"],
            },
        },
        {
            "name": "terminate_contract",
            "description": "Process early termination of a contract",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string"},
                    "termination_date": {"type": "string", "format": "date"},
                    "reason": {"type": "string"},
                    "settlement_amount": {"type": "number"},
                },
                "required": ["contract_id", "termination_date", "settlement_amount"],
            },
        },
        {
            "name": "renew_contract",
            "description": "Renew an expiring contract with new terms",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string"},
                    "new_duration_months": {"type": "integer"},
                    "new_terms": {"type": "object"},
                },
                "required": ["contract_id", "new_duration_months"],
            },
        },
        {
            "name": "get_payment_schedule",
            "description": "Retrieve the payment schedule for a contract",
            "parameters": {
                "type": "object",
                "properties": {"contract_id": {"type": "string"}},
                "required": ["contract_id"],
            },
        },
        {
            "name": "save_payment_schedule",
            "description": "Persist a computed payment schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string"},
                    "installments": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["contract_id", "installments"],
            },
        },
        {
            "name": "get_customer",
            "description": "Retrieve a customer by ID",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
        {
            "name": "list_customers",
            "description": "List customers with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string"},
                    "search": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 20},
                },
            },
        },
        {
            "name": "get_country_config",
            "description": "Retrieve country configuration (currency, tax rules)",
            "parameters": {
                "type": "object",
                "properties": {"country_code": {"type": "string"}},
                "required": ["country_code"],
            },
        },
    ],
}

# HTTP method mapping for each action
_ACTION_MAP: dict[str, tuple[str, str]] = {
    "create_contract": ("POST", "/api/v1/contracts"),
    "get_contract": ("GET", "/api/v1/contracts/{contract_id}"),
    "list_contracts": ("GET", "/api/v1/contracts"),
    "update_contract": ("PUT", "/api/v1/contracts/{contract_id}"),
    "activate_contract": ("POST", "/api/v1/contracts/{contract_id}/activate"),
    "amend_contract": ("POST", "/api/v1/contracts/{contract_id}/amend"),
    "terminate_contract": ("POST", "/api/v1/contracts/{contract_id}/terminate"),
    "renew_contract": ("POST", "/api/v1/contracts/{contract_id}/renew"),
    "get_payment_schedule": ("GET", "/api/v1/contracts/{contract_id}/schedule"),
    "save_payment_schedule": ("POST", "/api/v1/contracts/{contract_id}/schedule/generate"),
    "get_customer": ("GET", "/api/v1/customers/{customer_id}"),
    "list_customers": ("GET", "/api/v1/customers"),
    "get_country_config": ("GET", "/api/v1/countries/{country_code}/config"),
}


async def invoke(action: str, parameters: dict[str, Any], auth_token: str) -> dict[str, Any]:
    """Execute a Domain API action.

    Args:
        action: The action name from TOOL_SPEC.
        parameters: The action parameters.
        auth_token: JWT token for authorization.

    Returns:
        API response as a dictionary.
    """
    if action not in _ACTION_MAP:
        return {"error": f"Unknown action: {action}"}

    method, path_template = _ACTION_MAP[action]

    # Build path by substituting path parameters
    path_params = {}
    query_params = {}
    body = {}

    for key, value in parameters.items():
        if f"{{{key}}}" in path_template:
            path_params[key] = value
        elif method == "GET":
            query_params[key] = value
        else:
            body[key] = value

    path = path_template.format(**path_params)
    url = f"{DOMAIN_API_BASE_URL}{path}"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=body)
            else:
                return {"error": f"Unsupported method: {method}"}

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API error {e.response.status_code}: {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}

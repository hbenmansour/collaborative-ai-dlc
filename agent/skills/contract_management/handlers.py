"""Request handlers for the Contract Management skill.

Provides the programmatic interface that the agent orchestrator uses
to invoke skill actions. Each handler maps to a supported intent and
orchestrates calls to the Domain API tool.
"""

from typing import Any

from agent.tools.domain_api_tool import invoke as api_invoke


async def handle_request(intent: str, parameters: dict[str, Any], auth_token: str) -> dict[str, Any]:
    """Route a skill request to the appropriate handler.

    Args:
        intent: The classified intent (e.g., 'query_contract', 'portfolio_summary').
        parameters: Intent-specific parameters from the agent.
        auth_token: JWT token for Domain API authorization.

    Returns:
        Structured response dictionary.
    """
    handlers = {
        "create_contract": _handle_create_contract,
        "query_contract": _handle_query_contract,
        "list_contracts": _handle_list_contracts,
        "portfolio_summary": _handle_portfolio_summary,
        "contract_search": _handle_contract_search,
    }
    handler = handlers.get(intent)
    if not handler:
        return {"error": f"Unsupported intent: {intent}", "supported": list(handlers.keys())}
    return await handler(parameters, auth_token)


async def _handle_create_contract(params: dict[str, Any], token: str) -> dict[str, Any]:
    """Create a new draft contract via Domain API.

    Required params: lease_type, customer_id, country_code, asset_value, duration_months.
    """
    required = ["lease_type", "customer_id", "country_code", "asset_value", "duration_months"]
    missing = [f for f in required if f not in params]
    if missing:
        return {"error": "missing_fields", "missing": missing, "message": f"Please provide: {', '.join(missing)}"}

    result = await api_invoke("create_contract", params, token)
    if "error" in result:
        return result
    return {"status": "created", "contract": result}


async def _handle_query_contract(params: dict[str, Any], token: str) -> dict[str, Any]:
    """Retrieve a single contract by ID."""
    contract_id = params.get("contract_id")
    if not contract_id:
        return {"error": "missing_fields", "missing": ["contract_id"]}

    result = await api_invoke("get_contract", {"contract_id": contract_id}, token)
    if "error" in result:
        return result
    return {"contract": result}


async def _handle_list_contracts(params: dict[str, Any], token: str) -> dict[str, Any]:
    """List contracts with optional filters (status, lease_type, customer, country)."""
    filters = {k: v for k, v in params.items() if v is not None}
    result = await api_invoke("list_contracts", filters, token)
    if "error" in result:
        return result
    return {"contracts": result}


async def _handle_portfolio_summary(params: dict[str, Any], token: str) -> dict[str, Any]:
    """Generate portfolio summary by fetching all contracts and aggregating.

    Groups by status and lease_type to provide a high-level overview.
    """
    filters = {k: v for k, v in params.items() if v is not None}
    filters.setdefault("page_size", 1000)

    result = await api_invoke("list_contracts", filters, token)
    if "error" in result:
        return result

    contracts = result if isinstance(result, list) else result.get("items", [])

    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    total_value = 0.0

    for c in contracts:
        status = c.get("status", "unknown")
        lease_type = c.get("lease_type", "unknown")
        value = float(c.get("asset_value", 0) or 0)

        by_status[status] = by_status.get(status, 0) + 1
        by_type[lease_type] = by_type.get(lease_type, 0) + 1
        total_value += value

    return {
        "total_contracts": len(contracts),
        "total_asset_value": round(total_value, 2),
        "by_status": by_status,
        "by_lease_type": by_type,
    }


async def _handle_contract_search(params: dict[str, Any], token: str) -> dict[str, Any]:
    """Search contracts by various criteria including text search."""
    search_params: dict[str, Any] = {}
    if params.get("status"):
        search_params["status"] = params["status"]
    if params.get("lease_type"):
        search_params["lease_type"] = params["lease_type"]
    if params.get("customer_id"):
        search_params["customer_id"] = params["customer_id"]
    if params.get("country_code"):
        search_params["country_code"] = params["country_code"]
    if params.get("page"):
        search_params["page"] = params["page"]
    if params.get("page_size"):
        search_params["page_size"] = params["page_size"]

    result = await api_invoke("list_contracts", search_params, token)
    if "error" in result:
        return result
    return {"contracts": result}

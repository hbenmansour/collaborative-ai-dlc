"""Contract Management skill for Bedrock AgentCore.

Handles contract queries, portfolio summaries, and contract creation
via natural language conversation. This skill uses the Domain API tool
for CRUD operations and provides the agent with business context for
contract-related interactions.
"""

from .handlers import handle_request
from .instruction import SKILL_INSTRUCTION

SKILL_CONFIG = {
    "skill_name": "contract-management",
    "description": (
        "Handles contract queries, portfolio summaries, and contract creation "
        "via conversation. Supports natural language questions like "
        "'show me all contracts expiring next month' or "
        "'create a new vehicle lease for customer X'."
    ),
    "instruction": SKILL_INSTRUCTION,
    "tools_required": ["domain-api"],
    "supported_intents": [
        "create_contract",
        "query_contract",
        "list_contracts",
        "portfolio_summary",
        "contract_search",
    ],
}

__all__ = ["SKILL_CONFIG", "SKILL_INSTRUCTION", "handle_request"]

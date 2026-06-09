"""Skill handler for payment-calculation.

Defines the AgentCore skill configuration including tool references
and the instruction prompt used by the orchestrator agent.
"""

from agent.skills.payment_calculation import SKILL_CONFIG
from agent.skills.payment_calculation.instruction import INSTRUCTION


def get_skill_definition() -> dict:
    """Return the complete skill definition for AgentCore registration."""
    return {
        **SKILL_CONFIG,
        "instruction": INSTRUCTION,
        "input_schema": {
            "type": "object",
            "properties": {
                "contract_id": {
                    "type": "string",
                    "description": "UUID of the contract to generate a schedule for",
                },
                "method": {
                    "type": "string",
                    "enum": ["straight_line", "effective_interest"],
                    "description": "Amortization method. Defaults to effective_interest.",
                    "default": "effective_interest",
                },
                "display_currency": {
                    "type": "string",
                    "description": "Optional currency code for display conversion",
                },
            },
            "required": ["contract_id"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "schedule_id": {"type": "string"},
                "contract_id": {"type": "string"},
                "total_installments": {"type": "integer"},
                "currency_code": {"type": "string"},
                "installments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "installment_number": {"type": "integer"},
                            "due_date": {"type": "string", "format": "date"},
                            "amount": {"type": "number"},
                            "principal": {"type": "number"},
                            "interest": {"type": "number"},
                        },
                    },
                },
            },
        },
    }

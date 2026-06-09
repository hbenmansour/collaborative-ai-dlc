"""Skill routing for Bedrock AgentCore orchestrator.

Routes incoming requests to the appropriate skill based on intent classification.
Skills encapsulate business rules; the agent delegates to them.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SkillName(str, Enum):
    CONTRACT_MANAGEMENT = "contract-management"
    CONTRACT_LIFECYCLE = "contract-lifecycle"
    PAYMENT_CALCULATION = "payment-calculation"


@dataclass
class SkillDefinition:
    name: SkillName
    description: str
    intent_keywords: list[str]
    required_tools: list[str]


SKILL_REGISTRY: dict[SkillName, SkillDefinition] = {
    SkillName.CONTRACT_MANAGEMENT: SkillDefinition(
        name=SkillName.CONTRACT_MANAGEMENT,
        description="Contract queries, portfolio summaries, creation via conversation",
        intent_keywords=[
            "create contract", "new lease", "list contracts", "find contract",
            "show contracts", "portfolio", "contract summary", "search",
        ],
        required_tools=["domain-api"],
    ),
    SkillName.CONTRACT_LIFECYCLE: SkillDefinition(
        name=SkillName.CONTRACT_LIFECYCLE,
        description="Activation checks, termination penalties, renewal calculations, amendments",
        intent_keywords=[
            "activate", "terminate", "early termination", "penalty",
            "renew", "renewal", "amend", "amendment", "settlement",
        ],
        required_tools=["domain-api", "code-interpreter"],
    ),
    SkillName.PAYMENT_CALCULATION: SkillDefinition(
        name=SkillName.PAYMENT_CALCULATION,
        description="Amortization schedules, payment calculations, interest split",
        intent_keywords=[
            "payment schedule", "amortization", "installment", "calculate payment",
            "interest", "principal", "schedule", "billing",
        ],
        required_tools=["domain-api", "code-interpreter"],
    ),
}


def route_to_skill(user_input: str) -> SkillName | None:
    """Route user input to the most appropriate skill based on keyword matching.

    In production, this would use the LLM's built-in routing via skill descriptions.
    This function serves as a fallback/validation layer.

    Args:
        user_input: The user's natural language input.

    Returns:
        The matched SkillName or None if no skill matches.
    """
    input_lower = user_input.lower()
    best_match: SkillName | None = None
    best_score = 0

    for skill_name, definition in SKILL_REGISTRY.items():
        score = sum(1 for kw in definition.intent_keywords if kw in input_lower)
        if score > best_score:
            best_score = score
            best_match = skill_name

    return best_match


def get_skill_config(skill_name: SkillName) -> dict[str, Any]:
    """Get the configuration for a specific skill.

    Args:
        skill_name: The skill to retrieve configuration for.

    Returns:
        Skill configuration dictionary for AgentCore registration.
    """
    definition = SKILL_REGISTRY[skill_name]
    return {
        "skill_name": definition.name.value,
        "description": definition.description,
        "tools": definition.required_tools,
    }


def get_all_skill_configs() -> list[dict[str, Any]]:
    """Get configurations for all registered skills."""
    return [get_skill_config(name) for name in SKILL_REGISTRY]

"""Payment Calculation Skill for Bedrock AgentCore.

Encapsulates business rules for amortization schedule generation,
principal/interest split, multi-currency calculations, and residual value handling.
Delegates deterministic computations to the code interpreter tool.
"""

SKILL_NAME = "payment-calculation"

SKILL_CONFIG = {
    "name": SKILL_NAME,
    "description": (
        "Generates amortization/payment schedules for lease contracts. "
        "Supports straight-line and effective interest methods, "
        "monthly/quarterly/annual frequencies, multi-currency, and residual values."
    ),
    "tools": ["code_interpreter", "domain_api"],
    "intent_patterns": [
        "generate payment schedule",
        "calculate amortization",
        "payment plan",
        "installment breakdown",
        "principal interest split",
        "recalculate schedule",
    ],
}

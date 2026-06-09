"""Penalty calculation script for Bedrock AgentCore code interpreter.

Executed by the code interpreter tool to compute early termination
penalties. Configurable formula per lease type.
"""

from decimal import Decimal, ROUND_HALF_UP


PENALTY_CONFIG = {
    "vehicle": {"rate": Decimal("0.03"), "type": "percentage", "minimum": Decimal("500")},
    "equipment": {"rate": Decimal("0.05"), "type": "percentage", "minimum": Decimal("1000")},
    "financial": {"rate": Decimal("0.02"), "type": "percentage_plus_interest", "interest_months": 3},
}


def calculate_penalty(
    lease_type: str,
    outstanding_principal: float,
    annual_interest_rate: float = 0.0,
    remaining_months: int = 0,
) -> dict:
    """Calculate early termination penalty.

    Args:
        lease_type: One of 'vehicle', 'equipment', 'financial'.
        outstanding_principal: Remaining unpaid principal.
        annual_interest_rate: Contract annual interest rate (for financial type).
        remaining_months: Months left on contract (for context).

    Returns:
        Dict with penalty breakdown.
    """
    config = PENALTY_CONFIG.get(lease_type, PENALTY_CONFIG["vehicle"])
    principal = Decimal(str(outstanding_principal))
    penalty_type = config["type"]

    if penalty_type == "percentage":
        penalty = (principal * config["rate"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        penalty = max(penalty, config["minimum"])
    elif penalty_type == "percentage_plus_interest":
        base = (principal * config["rate"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        months = config["interest_months"]
        interest_portion = (
            principal * Decimal(str(annual_interest_rate)) * Decimal(str(months)) / Decimal("12")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        penalty = base + interest_portion
    else:
        penalty = Decimal("0")

    return {
        "lease_type": lease_type,
        "outstanding_principal": float(principal),
        "penalty_type": penalty_type,
        "penalty_rate": float(config["rate"]),
        "penalty_amount": float(penalty),
        "remaining_months": remaining_months,
    }


# Allow direct invocation by code interpreter
if __name__ == "__main__":
    import json
    import sys

    args = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    result = calculate_penalty(
        lease_type=args.get("lease_type", "vehicle"),
        outstanding_principal=args.get("outstanding_principal", 0),
        annual_interest_rate=args.get("annual_interest_rate", 0),
        remaining_months=args.get("remaining_months", 0),
    )
    print(json.dumps(result, indent=2))

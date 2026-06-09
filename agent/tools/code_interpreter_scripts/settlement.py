"""Settlement calculation script for Bedrock AgentCore code interpreter.

Computes the final settlement amount for early termination:
  settlement = outstanding_principal + penalty - deposit_held
"""

from decimal import Decimal, ROUND_HALF_UP


def calculate_settlement(
    outstanding_principal: float,
    penalty_amount: float,
    deposit_held: float = 0.0,
    accrued_interest: float = 0.0,
    other_fees: float = 0.0,
) -> dict:
    """Calculate final settlement amount.

    Args:
        outstanding_principal: Remaining unpaid principal.
        penalty_amount: Early termination penalty (from penalty_calculator).
        deposit_held: Security deposit held by lessor.
        accrued_interest: Interest accrued but not yet billed.
        other_fees: Any additional fees (admin, processing).

    Returns:
        Dict with settlement breakdown.
    """
    principal = Decimal(str(outstanding_principal))
    penalty = Decimal(str(penalty_amount))
    deposit = Decimal(str(deposit_held))
    interest = Decimal(str(accrued_interest))
    fees = Decimal(str(other_fees))

    gross = principal + penalty + interest + fees
    net_settlement = (gross - deposit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "outstanding_principal": float(principal),
        "penalty_amount": float(penalty),
        "accrued_interest": float(interest),
        "other_fees": float(fees),
        "gross_amount": float(gross),
        "deposit_held": float(deposit),
        "net_settlement": float(max(net_settlement, Decimal("0"))),
        "refund_to_lessee": float(abs(net_settlement)) if net_settlement < 0 else 0.0,
    }


# Allow direct invocation by code interpreter
if __name__ == "__main__":
    import json
    import sys

    args = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    result = calculate_settlement(
        outstanding_principal=args.get("outstanding_principal", 0),
        penalty_amount=args.get("penalty_amount", 0),
        deposit_held=args.get("deposit_held", 0),
        accrued_interest=args.get("accrued_interest", 0),
        other_fees=args.get("other_fees", 0),
    )
    print(json.dumps(result, indent=2))

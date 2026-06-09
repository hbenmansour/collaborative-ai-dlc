"""Code Interpreter tool configuration for Bedrock AgentCore.

Defines the code interpreter tool used for deterministic financial
calculations (amortization, penalties, settlements).
"""

TOOL_SPEC = {
    "name": "code-interpreter",
    "description": (
        "Execute Python code for deterministic financial calculations. "
        "Use for amortization schedules, penalty formulas, settlement amounts, "
        "and currency conversions."
    ),
    "type": "code_interpreter",
    "configuration": {
        "runtime": "python3",
        "timeout_seconds": 30,
        "allowed_modules": [
            "math",
            "decimal",
            "datetime",
            "json",
        ],
    },
}

# Pre-built calculation scripts the agent can invoke via code interpreter
CALCULATION_SCRIPTS = {
    "amortization_straight_line": """\
from decimal import Decimal, ROUND_HALF_UP

def calculate_straight_line(principal, rate_annual, duration_months, frequency):
    \"\"\"Straight-line amortization: equal installments.\"\"\"
    periods = {"monthly": duration_months, "quarterly": duration_months // 3, "annually": duration_months // 12}
    n = periods[frequency]
    rate_period = Decimal(str(rate_annual)) / Decimal("12") * ({"monthly": 1, "quarterly": 3, "annually": 12}[frequency])
    principal = Decimal(str(principal))
    total_interest = principal * Decimal(str(rate_annual)) * Decimal(str(duration_months)) / Decimal("12")
    installment_principal = (principal / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    installment_interest = (total_interest / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    installment_total = installment_principal + installment_interest
    schedule = []
    for i in range(1, n + 1):
        schedule.append({
            "period": i,
            "principal": float(installment_principal),
            "interest": float(installment_interest),
            "total": float(installment_total),
            "remaining_principal": float(principal - installment_principal * i),
        })
    return schedule
""",
    "amortization_effective_interest": """\
from decimal import Decimal, ROUND_HALF_UP

def calculate_effective_interest(principal, rate_annual, duration_months, frequency):
    \"\"\"Effective interest method: declining balance.\"\"\"
    periods = {"monthly": duration_months, "quarterly": duration_months // 3, "annually": duration_months // 12}
    n = periods[frequency]
    months_per_period = {"monthly": 1, "quarterly": 3, "annually": 12}[frequency]
    rate_period = Decimal(str(rate_annual)) * months_per_period / Decimal("12")
    principal = Decimal(str(principal))
    # PMT formula
    r = rate_period
    pmt = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    pmt = pmt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    balance = principal
    schedule = []
    for i in range(1, n + 1):
        interest = (balance * r).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        principal_portion = pmt - interest
        balance -= principal_portion
        schedule.append({
            "period": i,
            "principal": float(principal_portion),
            "interest": float(interest),
            "total": float(pmt),
            "remaining_principal": float(max(balance, Decimal("0"))),
        })
    return schedule
""",
    "penalty_calculation": """\
from decimal import Decimal, ROUND_HALF_UP

def calculate_termination_penalty(outstanding_principal, penalty_rate, deposit_held, penalty_type="percentage"):
    \"\"\"Calculate early termination penalty and settlement.\"\"\"
    outstanding = Decimal(str(outstanding_principal))
    deposit = Decimal(str(deposit_held))
    if penalty_type == "percentage":
        penalty = (outstanding * Decimal(str(penalty_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif penalty_type == "fixed":
        penalty = Decimal(str(penalty_rate))
    else:
        penalty = Decimal("0")
    settlement = outstanding + penalty - deposit
    return {
        "outstanding_principal": float(outstanding),
        "penalty_amount": float(penalty),
        "deposit_held": float(deposit),
        "settlement_amount": float(max(settlement, Decimal("0"))),
    }
""",
}

"""Amortization schedule calculator for the Bedrock AgentCore code interpreter.

Supports:
- Straight-line amortization (equal installments)
- Effective interest / declining balance (annuity formula)
- Monthly, quarterly, and annual payment frequencies
- Residual value handling
- Multi-currency (pass-through; conversion handled by caller)

Usage (invoked by code interpreter):
    result = generate_schedule(
        asset_value=50000,
        down_payment=5000,
        residual_value=3000,
        duration_months=36,
        annual_interest_rate=5.5,
        frequency="monthly",
        method="effective_interest",
        start_date="2026-01-15",
        currency_code="USD",
    )
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal


def _periods_per_year(frequency: str) -> int:
    return {"monthly": 12, "quarterly": 4, "annually": 1}[frequency]


def _add_period(d: date, frequency: str) -> date:
    """Advance date by one payment period."""
    if frequency == "monthly":
        month = d.month + 1
        year = d.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    elif frequency == "quarterly":
        month = d.month + 3
        year = d.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    else:  # annually
        try:
            return d.replace(year=d.year + 1)
        except ValueError:
            return date(d.year + 1, d.month, d.day - 1)


def _round2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _num_installments(duration_months: int, frequency: str) -> int:
    periods_per_year = _periods_per_year(frequency)
    months_per_period = 12 // periods_per_year
    return duration_months // months_per_period


def generate_straight_line(
    financed_amount: Decimal,
    residual_value: Decimal,
    num_installments: int,
    annual_rate: Decimal,
    frequency: str,
    start_date: date,
) -> list[dict]:
    """Straight-line: equal total installments, interest distributed evenly."""
    total_interest = financed_amount * annual_rate * Decimal(num_installments) / Decimal(_periods_per_year(frequency)) / Decimal(100)
    total_to_pay = financed_amount - residual_value + total_interest
    installment_amount = _round2(total_to_pay / Decimal(num_installments))
    principal_per_period = _round2((financed_amount - residual_value) / Decimal(num_installments))
    interest_per_period = _round2(total_interest / Decimal(num_installments))

    installments = []
    due = start_date
    cumulative_principal = Decimal("0")
    cumulative_interest = Decimal("0")

    for i in range(1, num_installments + 1):
        due = _add_period(due, frequency) if i == 1 else _add_period(due, frequency)
        if i < num_installments:
            due_date_current = due if i > 1 else _add_period(start_date, frequency)
        else:
            due_date_current = due

        p = principal_per_period
        intr = interest_per_period

        # Adjust final installment for rounding
        if i == num_installments:
            p = (financed_amount - residual_value) - cumulative_principal
            intr = total_interest - cumulative_interest

        cumulative_principal += p
        cumulative_interest += intr

        installments.append({
            "installment_number": i,
            "due_date": str(due),
            "amount": str(_round2(p + intr)),
            "principal": str(_round2(p)),
            "interest": str(_round2(intr)),
        })

    return installments


def generate_effective_interest(
    financed_amount: Decimal,
    residual_value: Decimal,
    num_installments: int,
    annual_rate: Decimal,
    frequency: str,
    start_date: date,
) -> list[dict]:
    """Effective interest (annuity): fixed installment, declining interest."""
    periods_per_year = _periods_per_year(frequency)
    periodic_rate = annual_rate / Decimal(100) / Decimal(periods_per_year)
    principal_to_amortize = financed_amount - residual_value

    # Annuity formula: PMT = P * r / (1 - (1+r)^-n)
    if periodic_rate == 0:
        pmt = _round2(principal_to_amortize / Decimal(num_installments))
    else:
        one_plus_r_n = (1 + periodic_rate) ** num_installments
        pmt = _round2(principal_to_amortize * periodic_rate * one_plus_r_n / (one_plus_r_n - 1))

    installments = []
    balance = principal_to_amortize
    due = start_date
    cumulative_principal = Decimal("0")

    for i in range(1, num_installments + 1):
        due = _add_period(due, frequency) if i == 1 else _add_period(due, frequency)
        if i < num_installments:
            due_date_current = due if i > 1 else _add_period(start_date, frequency)
        else:
            due_date_current = due

        interest = _round2(balance * periodic_rate)
        principal = pmt - interest

        # Final installment: clear remaining balance
        if i == num_installments:
            principal = balance
            interest = _round2(balance * periodic_rate)
            pmt = principal + interest

        balance -= principal
        cumulative_principal += principal

        installments.append({
            "installment_number": i,
            "due_date": str(due),
            "amount": str(_round2(principal + interest)),
            "principal": str(_round2(principal)),
            "interest": str(_round2(interest)),
        })

    return installments


def generate_schedule(
    asset_value: float,
    down_payment: float = 0,
    residual_value: float = 0,
    duration_months: int = 12,
    annual_interest_rate: float = 0,
    frequency: str = "monthly",
    method: str = "effective_interest",
    start_date: str = "2026-01-01",
    currency_code: str = "USD",
    exchange_rate: float = 1.0,
) -> dict:
    """Generate a complete amortization schedule.

    Args:
        asset_value: Total asset value.
        down_payment: Upfront payment reducing financed amount.
        residual_value: Residual/balloon value at end of lease.
        duration_months: Lease duration in months.
        annual_interest_rate: Annual interest rate as percentage (e.g., 5.5).
        frequency: Payment frequency - monthly, quarterly, or annually.
        method: Amortization method - straight_line or effective_interest.
        start_date: Contract start date (ISO format YYYY-MM-DD).
        currency_code: Currency code for the schedule.
        exchange_rate: Exchange rate for display currency conversion (1.0 = no conversion).

    Returns:
        Dict with schedule metadata and installments list.
    """
    if frequency not in ("monthly", "quarterly", "annually"):
        raise ValueError(f"Invalid frequency: {frequency}. Must be monthly, quarterly, or annually.")
    if method not in ("straight_line", "effective_interest"):
        raise ValueError(f"Invalid method: {method}. Must be straight_line or effective_interest.")

    av = Decimal(str(asset_value))
    dp = Decimal(str(down_payment))
    rv = Decimal(str(residual_value))
    rate = Decimal(str(annual_interest_rate))
    ex_rate = Decimal(str(exchange_rate))

    financed_amount = av - dp
    if financed_amount <= 0:
        raise ValueError("Financed amount (asset_value - down_payment) must be positive.")

    num_inst = _num_installments(duration_months, frequency)
    if num_inst <= 0:
        raise ValueError("Duration too short for the given frequency.")

    sd = date.fromisoformat(start_date)

    # If rate is 0, use straight-line regardless
    if rate == 0:
        method = "straight_line"

    if method == "straight_line":
        installments = generate_straight_line(financed_amount, rv, num_inst, rate, frequency, sd)
    else:
        installments = generate_effective_interest(financed_amount, rv, num_inst, rate, frequency, sd)

    # Apply exchange rate if not 1.0
    if ex_rate != 1:
        for inst in installments:
            inst["amount"] = str(_round2(Decimal(inst["amount"]) * ex_rate))
            inst["principal"] = str(_round2(Decimal(inst["principal"]) * ex_rate))
            inst["interest"] = str(_round2(Decimal(inst["interest"]) * ex_rate))

    total_amount = sum(Decimal(i["amount"]) for i in installments)
    total_principal = sum(Decimal(i["principal"]) for i in installments)
    total_interest = sum(Decimal(i["interest"]) for i in installments)

    return {
        "currency_code": currency_code,
        "method": method,
        "frequency": frequency,
        "total_installments": num_inst,
        "financed_amount": str(_round2(financed_amount * ex_rate)),
        "residual_value": str(_round2(rv * ex_rate)),
        "total_amount": str(_round2(total_amount)),
        "total_principal": str(_round2(total_principal)),
        "total_interest": str(_round2(total_interest)),
        "installments": installments,
    }


# Allow direct invocation by code interpreter
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        # Default example
        params = {
            "asset_value": 50000,
            "down_payment": 5000,
            "residual_value": 3000,
            "duration_months": 36,
            "annual_interest_rate": 5.5,
            "frequency": "monthly",
            "method": "effective_interest",
            "start_date": "2026-01-15",
            "currency_code": "USD",
        }
    result = generate_schedule(**params)
    print(json.dumps(result, indent=2))

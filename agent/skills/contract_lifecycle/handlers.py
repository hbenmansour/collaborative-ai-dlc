"""Business logic handlers for contract lifecycle operations.

Each handler validates preconditions, applies business rules, and
orchestrates calls to the Domain API and code interpreter.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from agent.skills.contract_lifecycle import ACTIVATION_CHECKLIST, PENALTY_RULES


def check_activation_readiness(contract: dict[str, Any], customer: dict[str, Any]) -> dict[str, Any]:
    """Check if a contract is ready for activation.

    Args:
        contract: Contract data from Domain API.
        customer: Customer data from Domain API.

    Returns:
        Dict with ready (bool), passed checks, and failed checks.
    """
    results: dict[str, bool] = {}

    # Contract must be in draft status
    results["contract_status_draft"] = contract.get("status") == "draft"

    # Customer KYC must be valid
    kyc_docs = customer.get("kyc_documents", [])
    results["customer_kyc_valid"] = any(
        doc.get("status") == "approved" and (
            not doc.get("expiry") or doc["expiry"] >= str(date.today())
        )
        for doc in kyc_docs
    ) if kyc_docs else False

    # Approvals required for high-value contracts
    asset_value = Decimal(str(contract.get("asset_value") or 0))
    if asset_value > Decimal("100000"):
        results["approvals_obtained"] = contract.get("manager_approved", False)
    else:
        results["approvals_obtained"] = True

    # Credit check
    results["credit_check_passed"] = customer.get("credit_status") != "failed"

    # Dates must be set
    results["dates_set"] = bool(contract.get("start_date") and contract.get("end_date"))

    # Terms must be complete
    terms = contract.get("terms") or {}
    results["terms_complete"] = all([
        terms.get("duration_months"),
        terms.get("interest_rate") is not None,
        terms.get("payment_frequency"),
        terms.get("currency_code"),
    ])

    # Asset value specified
    results["asset_value_specified"] = asset_value > 0

    passed = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]

    return {
        "ready": len(failed) == 0,
        "passed": passed,
        "failed": failed,
        "checklist": ACTIVATION_CHECKLIST,
    }


def calculate_termination_penalty(
    lease_type: str,
    outstanding_principal: Decimal,
    interest_rate: Decimal,
    deposit_held: Decimal = Decimal("0"),
) -> dict[str, Any]:
    """Calculate early termination penalty based on lease type.

    Args:
        lease_type: One of vehicle, equipment, financial.
        outstanding_principal: Remaining principal balance.
        interest_rate: Annual interest rate (decimal, e.g. 0.05).
        deposit_held: Security deposit held by lessor.

    Returns:
        Penalty breakdown with settlement amount.
    """
    rules = PENALTY_RULES.get(lease_type, PENALTY_RULES["vehicle"])
    principal = Decimal(str(outstanding_principal))
    rate = Decimal(str(rules["rate"]))

    if rules["type"] == "percentage":
        penalty = (principal * rate).quantize(Decimal("0.01"))
        minimum = Decimal(str(rules.get("minimum", 0)))
        penalty = max(penalty, minimum)
    elif rules["type"] == "percentage_plus_interest":
        base_penalty = (principal * rate).quantize(Decimal("0.01"))
        months = rules.get("interest_months", 3)
        remaining_interest = (
            principal * Decimal(str(interest_rate)) * Decimal(str(months)) / Decimal("12")
        ).quantize(Decimal("0.01"))
        penalty = base_penalty + remaining_interest
    else:
        penalty = Decimal("0")

    deposit = Decimal(str(deposit_held))
    settlement = principal + penalty - deposit

    return {
        "lease_type": lease_type,
        "outstanding_principal": float(principal),
        "penalty_rate": float(rate),
        "penalty_amount": float(penalty),
        "deposit_held": float(deposit),
        "settlement_amount": float(max(settlement, Decimal("0"))),
        "refund_due": float(abs(settlement)) if settlement < 0 else 0,
    }


def calculate_renewal_terms(
    contract: dict[str, Any],
    new_duration_months: int,
    new_interest_rate: float | None = None,
    new_frequency: str | None = None,
) -> dict[str, Any]:
    """Calculate renewal terms for an expiring contract.

    Args:
        contract: Current contract data.
        new_duration_months: Requested renewal duration.
        new_interest_rate: Optional new rate (defaults to current).
        new_frequency: Optional new payment frequency.

    Returns:
        Proposed renewal terms with validation.
    """
    errors: list[str] = []

    if contract.get("status") not in ("active", "expired"):
        errors.append(f"Contract status '{contract.get('status')}' cannot be renewed")

    if new_duration_months < 6:
        errors.append("Renewal duration must be at least 6 months")

    if errors:
        return {"valid": False, "errors": errors}

    current_terms = contract.get("terms") or {}
    current_end = contract.get("end_date", str(date.today()))
    renewal_start = str(date.fromisoformat(current_end) + timedelta(days=1)) if current_end else str(date.today())

    renewal_end = str(
        date.fromisoformat(renewal_start) + timedelta(days=new_duration_months * 30)
    )

    return {
        "valid": True,
        "renewal_start_date": renewal_start,
        "renewal_end_date": renewal_end,
        "duration_months": new_duration_months,
        "interest_rate": new_interest_rate or float(current_terms.get("interest_rate", 0)),
        "payment_frequency": new_frequency or current_terms.get("payment_frequency", "monthly"),
        "currency_code": current_terms.get("currency_code"),
        "original_contract_id": contract.get("id"),
    }


def analyze_amendment_impact(
    contract: dict[str, Any],
    changes: dict[str, Any],
    effective_date: str,
) -> dict[str, Any]:
    """Analyze the impact of amending contract terms.

    Args:
        contract: Current contract data.
        changes: Proposed field changes.
        effective_date: Date from which changes take effect.

    Returns:
        Impact analysis with before/after comparison.
    """
    errors: list[str] = []
    allowed_fields = {"payment_amount", "duration_months", "interest_rate", "payment_frequency"}

    if contract.get("status") != "active":
        errors.append("Only active contracts can be amended")

    invalid_fields = set(changes.keys()) - allowed_fields
    if invalid_fields:
        errors.append(f"Fields not allowed for amendment: {invalid_fields}")

    eff_date = date.fromisoformat(effective_date) if effective_date else None
    if eff_date and eff_date <= date.today():
        errors.append("Effective date must be in the future")

    if errors:
        return {"valid": False, "errors": errors}

    current_terms = contract.get("terms") or {}
    before = {k: current_terms.get(k) for k in changes}
    after = changes

    # Estimate remaining periods from effective date
    end_date = contract.get("end_date")
    remaining_months = 0
    if end_date and eff_date:
        delta = date.fromisoformat(end_date) - eff_date
        remaining_months = max(delta.days // 30, 1)

    return {
        "valid": True,
        "effective_date": effective_date,
        "before": before,
        "after": after,
        "remaining_months_affected": remaining_months,
        "requires_schedule_recalculation": True,
        "preserves_paid_history": True,
    }

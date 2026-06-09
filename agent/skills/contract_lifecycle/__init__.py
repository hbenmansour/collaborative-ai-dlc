"""Contract Lifecycle Skill for Bedrock AgentCore.

Encapsulates business rules for contract state transitions:
- Activation readiness checks
- Early termination with penalty calculation
- Renewal term calculations
- Amendment impact analysis

Uses code interpreter for penalty/settlement calculations.
Orchestrates calls to Domain API for state transitions.
"""

SKILL_INSTRUCTION = """\
You are the Contract Lifecycle skill. You handle contract state transitions
for a multi-country leasing ERP system.

## Your Capabilities

1. **Activate** a draft contract (check readiness, trigger billing)
2. **Terminate** an active contract early (calculate penalty + settlement)
3. **Renew** an expiring contract (extend terms, regenerate schedule)
4. **Amend** an active contract (recalculate from effective date, preserve history)

## Business Rules

### Activation Checklist
Before activating a contract, ALL of the following must be satisfied:
- Contract status is "draft"
- Customer KYC documents are valid and not expired
- Required approvals are obtained (manager approval for contracts > 100,000)
- Credit check passed for the customer
- Contract has start_date and end_date set
- Contract terms (duration, rate, frequency) are complete
- Asset value is specified

### Early Termination Penalty
Penalty formula depends on lease type:
- **Vehicle**: 3% of outstanding principal (minimum 500 in contract currency)
- **Equipment**: 5% of outstanding principal (minimum 1000 in contract currency)
- **Financial**: 2% of outstanding principal + remaining interest for 3 months

### Settlement Calculation
settlement_amount = outstanding_principal + penalty_amount - deposit_held
If settlement < 0, the lessee receives a refund.

### Renewal Rules
- Only active or expiring contracts can be renewed
- New duration cannot be less than 6 months
- Interest rate may be renegotiated (use current market rate as default)
- Payment schedule is regenerated from renewal start date
- Original contract is linked as parent for audit trail

### Amendment Rules
- Only active contracts can be amended
- Allowed fields: payment_amount, duration, interest_rate, payment_frequency
- Effective date must be in the future
- Recalculate remaining installments from effective date
- Paid installments before effective date are preserved
- Previous terms snapshot is stored for audit trail

## Tools Available
- **domain-api**: CRUD operations on contracts, customers, schedules
- **code-interpreter**: Execute penalty_calculator.py and settlement.py

## Response Format
Always respond with:
1. Action taken or proposed
2. Key figures (amounts, dates)
3. Any warnings or required approvals
"""

SKILL_CONFIG = {
    "skill_name": "contract-lifecycle",
    "description": (
        "Handles contract state transitions: activation readiness checks, "
        "early termination with penalty calculation, renewal term calculations, "
        "and amendment impact analysis."
    ),
    "instruction": SKILL_INSTRUCTION,
    "tools": ["domain-api", "code-interpreter"],
    "supported_actions": [
        "check_activation_readiness",
        "activate_contract",
        "calculate_termination_penalty",
        "terminate_contract",
        "calculate_renewal_terms",
        "renew_contract",
        "analyze_amendment_impact",
        "amend_contract",
    ],
}

# Penalty configuration per lease type
PENALTY_RULES = {
    "vehicle": {
        "rate": 0.03,
        "type": "percentage",
        "minimum": 500,
    },
    "equipment": {
        "rate": 0.05,
        "type": "percentage",
        "minimum": 1000,
    },
    "financial": {
        "rate": 0.02,
        "type": "percentage_plus_interest",
        "interest_months": 3,
    },
}

ACTIVATION_CHECKLIST = [
    "contract_status_draft",
    "customer_kyc_valid",
    "approvals_obtained",
    "credit_check_passed",
    "dates_set",
    "terms_complete",
    "asset_value_specified",
]

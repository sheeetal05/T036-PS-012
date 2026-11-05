from models import Policy, Member, Claim


# =========================================================
# BR-01: WAITING PERIOD
# =========================================================

def check_waiting_period(
    policy: Policy,
    member: Member,
    claim: Claim,
    accident_codes=None,
    specified_illnesses=None
):
    """Check whether a claim has completed all applicable waiting periods."""

    if accident_codes is None:
        accident_codes = []

    if specified_illnesses is None:
        specified_illnesses = []

    admission_date = claim.admission_date
    inception_date = policy.inception_date

    days_since_inception = (admission_date - inception_date).days

    # Accident claims skip the initial 30-day waiting period
    if claim.diagnosis_code in accident_codes:
        return True, "Eligible – accident exemption"

    # Initial 30-day waiting period
    if days_since_inception < 30:
        return False, "REJECTED: BR-01 Initial waiting period"

    # Calculate months since policy inception
    months_since_inception = (
        (admission_date.year - inception_date.year) * 12
        + admission_date.month
        - inception_date.month
    )

    # Specified illness waiting period: 24 months
    if (
        claim.diagnosis_code in specified_illnesses
        and months_since_inception < 24
    ):
        return False, "REJECTED: BR-01 Specified illness waiting period"

    # Pre-existing disease waiting period: 36 months
    if (
        claim.diagnosis_code in member.ped_list
        and months_since_inception < 36
    ):
        return False, "REJECTED: BR-01 PED waiting period"

    return True, "Eligible"


# =========================================================
# BR-02: ROOM RENT LIMIT & PROPORTIONATE DEDUCTION
# =========================================================

def get_room_rent_limit(policy: Policy, is_icu=False):
    """
    Calculate the maximum eligible room rent per day
    based on the policy plan.
    """

    plan = policy.plan.upper()

    if plan == "SILVER":
        limit = policy.sum_insured * 0.01

    elif plan == "GOLD":
        limit = policy.sum_insured * 0.02

    elif plan == "PLATINUM":
        return None  # No room rent limit

    else:
        raise ValueError("Invalid policy plan")

    # ICU limit is twice the normal room rent limit
    if is_icu:
        limit *= 2

    return limit


def calculate_proportionate_factor(
    policy: Policy,
    actual_room_rent: float,
    is_icu=False
):
    """
    Calculate the proportionate deduction factor.
    """

    if actual_room_rent <= 0:
        raise ValueError("Actual room rent must be greater than zero")

    room_limit = get_room_rent_limit(policy, is_icu)

    # PLATINUM has no room rent limit
    if room_limit is None:
        return 1.0, None

    # Room rent is within the allowed limit
    if actual_room_rent <= room_limit:
        return 1.0, room_limit

    # Room rent exceeds the limit
    factor = room_limit / actual_room_rent

    return factor, room_limit


def apply_proportionate_deduction(
    amount: float,
    proportionate_factor: float
):
    """Apply the proportionate deduction to an associated charge."""

    if amount < 0:
        raise ValueError("Amount cannot be negative")

    return amount * proportionate_factor
# =========================================================
# BR-03: DISEASE / PROCEDURE SUB-LIMITS
# =========================================================

def get_disease_sub_limit(policy: Policy, diagnosis_code: str):
    """
    Return the applicable disease/procedure sub-limit.
    PLATINUM plans have no disease sub-limits.
    """

    # PLATINUM has no sub-limits
    if policy.plan.upper() == "PLATINUM":
        return None

    diagnosis_code = diagnosis_code.upper()

    sub_limits = {
        "CATARACT": 40000,
        "KNEE_REPLACEMENT": 150000,
        "HERNIA": 60000
    }

    return sub_limits.get(diagnosis_code)


def apply_disease_sub_limit(
    policy: Policy,
    diagnosis_code: str,
    amount_after_room_deduction: float
):
    """
    Apply the disease/procedure sub-limit after
    the room proportionate deduction.
    """

    if amount_after_room_deduction < 0:
        raise ValueError("Amount cannot be negative")

    sub_limit = get_disease_sub_limit(policy, diagnosis_code)

    # No sub-limit applies
    if sub_limit is None:
        return amount_after_room_deduction, None

    # Insurance pays the lower amount
    eligible_amount = min(amount_after_room_deduction, sub_limit)

    return eligible_amount, sub_limit
# =========================================================
# BR-04: CO-PAY
# =========================================================

def calculate_age_on_date(date_of_birth, reference_date):
    """Calculate a person's age on a specific date."""

    age = reference_date.year - date_of_birth.year

    # Check whether the birthday has happened yet this year
    if (
        reference_date.month,
        reference_date.day
    ) < (
        date_of_birth.month,
        date_of_birth.day
    ):
        age -= 1

    return age


def calculate_copay_percentage(
    policy: Policy,
    member: Member,
    admission_date,
    hospital_zone: str
):
    """
    Calculate the total co-pay percentage.

    - Age 61 or above: 20%
    - Zone C hospital when policy zone is A: 10%
    - Maximum total: 30%
    """

    copay_percentage = 0

    # Calculate member's age on admission date
    age = calculate_age_on_date(
        member.date_of_birth,
        admission_date
    )

    # Age-based co-pay
    if age >= 61:
        copay_percentage += 20

    # Zone-based co-pay
    if (
        policy.zone.upper() == "A"
        and hospital_zone.upper() == "C"
    ):
        copay_percentage += 10

    # Maximum co-pay is 30%
    return min(copay_percentage, 30)


def apply_copay(eligible_amount: float, copay_percentage: float):
    """
    Calculate customer share and insurance payable
    after applying co-pay.
    """

    if eligible_amount < 0:
        raise ValueError("Eligible amount cannot be negative")

    customer_share = eligible_amount * (copay_percentage / 100)
    insurance_payable = eligible_amount - customer_share

    return customer_share, insurance_payable
    # =========================================================
# BR-05: NON-PAYABLES
# =========================================================

def calculate_non_payable_deduction(
    policy: Policy,
    total_bill: float,
    non_payable_amount: float,
    consumable_cover: bool = False
):
    """
    Calculate the deduction for non-payable items.

    - Consumables are deducted fully by default.
    - If CONSUMABLE_COVER rider exists, no deduction is made.
    - For PLATINUM, non-payable deduction is capped at 10% of total bill.
    """

    if total_bill < 0 or non_payable_amount < 0:
        raise ValueError("Amounts cannot be negative")

    # Consumable cover rider means no deduction
    if consumable_cover:
        return 0.0

    deduction = non_payable_amount

    # PLATINUM: deduction cannot exceed 10% of the total bill
    if policy.plan.upper() == "PLATINUM":
        maximum_deduction = total_bill * 0.10
        deduction = min(deduction, maximum_deduction)

    return deduction# =========================================================
# BR-06: PRE-AUTHORISATION & ENHANCEMENT
# =========================================================

def calculate_pre_auth_approval(
    eligible_estimated_bill: float,
    remaining_si: float
):
    """
    Calculate initial pre-authorisation approval.

    Approval = minimum of:
    - Eligible estimated bill
    - 60% of remaining Sum Insured
    - ₹2,00,000
    """

    if eligible_estimated_bill < 0 or remaining_si < 0:
        raise ValueError("Amounts cannot be negative")

    approval = min(
        eligible_estimated_bill,
        remaining_si * 0.60,
        200000
    )

    return approval


def validate_enhancement_request(
    request_date,
    discharge_date
):
    """
    Check whether an enhancement request was made
    before or on the discharge date.
    """

    if discharge_date is None:
        # If discharge has not happened yet, enhancement is allowed
        return True, "Enhancement request is valid"

    if request_date <= discharge_date:
        return True, "Enhancement request is valid"

    return False, "REJECTED: Enhancement request received after discharge"


def calculate_enhancement_approval(
    requested_amount: float,
    remaining_si: float
):
    """
    Enhancement can be approved up to the remaining
    available Sum Insured.
    """

    if requested_amount < 0 or remaining_si < 0:
        raise ValueError("Amounts cannot be negative")

    approved_amount = min(
        requested_amount,
        remaining_si
    )

    return approved_amount
# =========================================================
# BR-07: FINAL BILL & SETTLEMENT
# =========================================================

def calculate_final_settlement(
    final_bill: float,
    eligible_amount: float,
    copay_percentage: float,
    remaining_si: float,
    initial_approved_amount: float
):
    """
    Calculate the final insurance payable and customer share.

    The insurance payable is:
    eligible amount after co-pay, capped at remaining SI.
    """

    if (
        final_bill < 0
        or eligible_amount < 0
        or remaining_si < 0
        or initial_approved_amount < 0
    ):
        raise ValueError("Amounts cannot be negative")

    # Calculate co-pay
    copay_amount = eligible_amount * (copay_percentage / 100)

    # Amount payable by insurance after co-pay
    insurance_payable_before_cap = eligible_amount - copay_amount

    # Insurance cannot pay more than remaining SI
    insurance_payable = min(
        insurance_payable_before_cap,
        remaining_si
    )

    # Customer pays everything not paid by insurance
    customer_share = final_bill - insurance_payable

    # If final bill is lower than initial approval,
    # the unused approved amount is released
    released_amount = max(
        0,
        initial_approved_amount - insurance_payable
    )

    return {
        "final_bill": final_bill,
        "eligible_amount": eligible_amount,
        "copay_amount": copay_amount,
        "insurance_payable": insurance_payable,
        "customer_share": customer_share,
        "released_amount": released_amount
    }
# =========================================================
# BR-08: PRE & POST-HOSPITALISATION EXPENSES
# =========================================================

def calculate_pre_post_hospitalisation(
    admissible_claim: float,
    pre_expense: float,
    post_expense: float
):
    """
    Calculate the eligible pre and post-hospitalisation expenses.

    The combined amount is capped at 10% of the
    admissible hospitalisation claim.
    """

    if (
        admissible_claim < 0
        or pre_expense < 0
        or post_expense < 0
    ):
        raise ValueError("Amounts cannot be negative")

    maximum_allowed = admissible_claim * 0.10
    total_expenses = pre_expense + post_expense

    eligible_expenses = min(
        total_expenses,
        maximum_allowed
    )

    return {
        "pre_expense": pre_expense,
        "post_expense": post_expense,
        "total_submitted": total_expenses,
        "maximum_allowed": maximum_allowed,
        "eligible_expenses": eligible_expenses
    }
# =========================================================
# BR-09: SUM INSURED RESTORATION
# =========================================================

def check_restoration_eligibility(
    policy: Policy,
    previous_icd_chapters: list,
    new_icd_chapter: str,
    same_member_same_illness: bool
):
    """
    Check whether Sum Insured restoration can be used.

    Conditions:
    - Base Sum Insured must be exhausted.
    - Restoration can only happen once per policy year.
    - New claim must be for an unrelated illness
      (different ICD chapter).
    - Restored SI cannot be used for the same member's
      same illness.
    """

    # SI must be exhausted
    if policy.remaining_si > 0:
        return False, "SI is not exhausted"

    # Restoration can only be used once
    if policy.restoration_used:
        return False, "Restoration already used this policy year"

    # Same member + same illness is not eligible
    if same_member_same_illness:
        return False, "Same member's same illness cannot use restored SI"

    # New illness must belong to a different ICD chapter
    if new_icd_chapter in previous_icd_chapters:
        return False, "Claim is from an already used ICD chapter"

    return True, "Eligible for restoration"


def restore_sum_insured(policy: Policy):
    """
    Restore 100% of the base Sum Insured.
    """

    if policy.restoration_used:
        raise ValueError("Restoration has already been used")

    policy.remaining_si = policy.sum_insured
    policy.restoration_used = True

    return policy.remaining_si
# =========================================================
# BR-10: NO-CLAIM BONUS
# =========================================================

def add_no_claim_bonus(policy: Policy):
    """
    Add a 10% No-Claim Bonus for one claim-free year.

    The total bonus cannot exceed 50% of the base Sum Insured.
    """

    bonus_increment = policy.sum_insured * 0.10
    maximum_bonus = policy.sum_insured * 0.50

    policy.no_claim_bonus = min(
        policy.no_claim_bonus + bonus_increment,
        maximum_bonus
    )

    return policy.no_claim_bonus


def reduce_no_claim_bonus_at_renewal(policy: Policy):
    """
    Reduce the No-Claim Bonus by 10 percentage points
    when a claim has occurred during the policy year.
    """

    reduction = policy.sum_insured * 0.10

    policy.no_claim_bonus = max(
        0,
        policy.no_claim_bonus - reduction
    )

    return policy.no_claim_bonus
# =========================================================
# BR-11: QUERY TIMELINE & RESUBMISSION
# =========================================================

from datetime import timedelta


def check_query_response_time(
    query_time,
    response_time
):
    """
    Check whether the hospital responded to a query
    within the allowed 48-hour timeline.
    """

    if response_time < query_time:
        raise ValueError("Response time cannot be before query time")

    time_difference = response_time - query_time

    # Response at exactly 48 hours is valid
    if time_difference <= timedelta(hours=48):
        return True, "Query response received within 48 hours"

    return False, "REJECTED: Query response exceeded 48 hours"


def can_resubmit_pre_auth(resubmission_count: int):
    """
    A rejected pre-authorisation can be resubmitted once.
    """

    if resubmission_count < 0:
        raise ValueError("Resubmission count cannot be negative")

    return resubmission_count < 1

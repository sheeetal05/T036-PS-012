from datetime import timedelta
from src.models import Policy, Member


# =========================================================
# BR-01: WAITING PERIOD
# =========================================================

def check_waiting_period(
    policy,
    member,
    claim,
    accident_codes=None,
    specified_illnesses=None
):
    """
    Check whether a claim satisfies the applicable
    waiting period rules.
    """

    if accident_codes is None:
        accident_codes = []

    if specified_illnesses is None:
        specified_illnesses = []

    days_since_inception = (
        claim.admission_date - policy.inception_date
    ).days

    diagnosis = claim.diagnosis_code.upper()

    # Accident claims are exempt from the initial 30-day wait
    if diagnosis in [code.upper() for code in accident_codes]:
        return True, "Waiting period satisfied"

    # BR-01A: Initial waiting period - 30 days
    if days_since_inception < 30:
        return False, "REJECTED: Initial 30-day waiting period"

    # BR-01B: Specified illnesses - 24 months
    if diagnosis in [
        illness.upper() for illness in specified_illnesses
    ]:
        if days_since_inception < 730:
            return False, (
                "REJECTED: 24-month specified illness "
                "waiting period"
            )

    # BR-01C: PED - 36 months
    member_ped_list = getattr(member, "ped_list", [])

    if diagnosis in [
        disease.upper() for disease in member_ped_list
    ]:
        if days_since_inception < 1095:
            return False, (
                "REJECTED: 36-month PED waiting period"
            )

    return True, "Waiting period satisfied"


# =========================================================
# BR-02: ROOM RENT & PROPORTIONATE DEDUCTION
# =========================================================

def calculate_proportionate_factor(
    policy: Policy,
    actual_room_rent: float
):
    """
    Calculate room rent eligibility and proportionate factor.
    """

    if actual_room_rent < 0:
        raise ValueError("Room rent cannot be negative")

    plan = policy.plan.upper()

    # PLATINUM has no room rent limit
    if plan == "PLATINUM":
        return 1.0, None

    # SILVER: 1% of SI per day
    if plan == "SILVER":
        room_limit = policy.sum_insured * 0.01

    # GOLD: 2% of SI per day
    elif plan == "GOLD":
        room_limit = policy.sum_insured * 0.02

    else:
        raise ValueError("Invalid policy plan")

    # Room rent within limit
    if actual_room_rent <= room_limit:
        return 1.0, room_limit

    # Proportionate reduction factor
    factor = room_limit / actual_room_rent

    return factor, room_limit


def apply_proportionate_deduction(
    amount: float,
    proportionate_factor: float
):
    """Apply room proportionate deduction."""

    if amount < 0:
        raise ValueError("Amount cannot be negative")

    return amount * proportionate_factor


# =========================================================
# BR-03: DISEASE / PROCEDURE SUB-LIMITS
# =========================================================

def get_disease_sub_limit(
    policy: Policy,
    diagnosis_code: str
):
    """Return the applicable disease/procedure sub-limit."""

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
    """Apply disease sub-limit after room deduction."""

    if amount_after_room_deduction < 0:
        raise ValueError("Amount cannot be negative")

    sub_limit = get_disease_sub_limit(
        policy,
        diagnosis_code
    )

    if sub_limit is None:
        return amount_after_room_deduction, None

    eligible_amount = min(
        amount_after_room_deduction,
        sub_limit
    )

    return eligible_amount, sub_limit


# =========================================================
# BR-04: CO-PAY
# =========================================================

def calculate_age_on_date(
    date_of_birth,
    reference_date
):
    """Calculate age on a specific date."""

    age = reference_date.year - date_of_birth.year

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
    """Calculate total co-pay percentage."""

    copay_percentage = 0

    age = calculate_age_on_date(
        member.date_of_birth,
        admission_date
    )

    # Age 61 or above
    if age >= 61:
        copay_percentage += 20

    # Zone C hospital with Zone A policy
    if (
        policy.zone.upper() == "A"
        and hospital_zone.upper() == "C"
    ):
        copay_percentage += 10

    # Maximum co-pay is 30%
    return min(copay_percentage, 30)


def apply_copay(
    eligible_amount: float,
    copay_percentage: float
):
    """Calculate customer share and insurance payable."""

    if eligible_amount < 0:
        raise ValueError("Eligible amount cannot be negative")

    customer_share = (
        eligible_amount * (copay_percentage / 100)
    )

    insurance_payable = (
        eligible_amount - customer_share
    )

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
    """Calculate non-payable deduction."""

    if total_bill < 0 or non_payable_amount < 0:
        raise ValueError("Amounts cannot be negative")

    # Consumable cover means no deduction
    if consumable_cover:
        return 0.0

    deduction = non_payable_amount

    # PLATINUM deduction capped at 10% of bill
    if policy.plan.upper() == "PLATINUM":
        maximum_deduction = total_bill * 0.10
        deduction = min(
            deduction,
            maximum_deduction
        )

    return deduction


# =========================================================
# BR-06: PRE-AUTHORISATION & ENHANCEMENT
# =========================================================

def calculate_pre_auth_approval(
    eligible_estimated_bill: float,
    remaining_si: float
):
    """Calculate initial pre-authorisation approval."""

    if (
        eligible_estimated_bill < 0
        or remaining_si < 0
    ):
        raise ValueError("Amounts cannot be negative")

    return min(
        eligible_estimated_bill,
        remaining_si * 0.60,
        200000
    )


def validate_enhancement_request(
    request_date,
    discharge_date
):
    """Check whether enhancement was requested on time."""

    if discharge_date is None:
        return True, "Enhancement request is valid"

    if request_date <= discharge_date:
        return True, "Enhancement request is valid"

    return (
        False,
        "REJECTED: Enhancement request received after discharge"
    )


def calculate_enhancement_approval(
    requested_amount: float,
    remaining_si: float
):
    """Calculate enhancement approval."""

    if (
        requested_amount < 0
        or remaining_si < 0
    ):
        raise ValueError("Amounts cannot be negative")

    return min(
        requested_amount,
        remaining_si
    )


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
    """Calculate final settlement."""

    if (
        final_bill < 0
        or eligible_amount < 0
        or remaining_si < 0
        or initial_approved_amount < 0
    ):
        raise ValueError("Amounts cannot be negative")

    copay_amount = (
        eligible_amount * (copay_percentage / 100)
    )

    insurance_before_cap = (
        eligible_amount - copay_amount
    )

    insurance_payable = min(
        insurance_before_cap,
        remaining_si
    )

    customer_share = (
        final_bill - insurance_payable
    )

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
# BR-08: PRE & POST-HOSPITALISATION
# =========================================================

def calculate_pre_post_hospitalisation(
    admissible_claim: float,
    pre_expense: float,
    post_expense: float
):
    """Calculate eligible pre and post-hospitalisation expenses."""

    if (
        admissible_claim < 0
        or pre_expense < 0
        or post_expense < 0
    ):
        raise ValueError("Amounts cannot be negative")

    maximum_allowed = admissible_claim * 0.10

    total_expenses = (
        pre_expense + post_expense
    )

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
    """Check restoration eligibility."""

    if policy.remaining_si > 0:
        return False, "SI is not exhausted"

    if policy.restoration_used:
        return (
            False,
            "Restoration already used this policy year"
        )

    if same_member_same_illness:
        return (
            False,
            "Same member's same illness cannot use restored SI"
        )

    if new_icd_chapter in previous_icd_chapters:
        return (
            False,
            "Claim is from an already used ICD chapter"
        )

    return True, "Eligible for restoration"


def restore_sum_insured(policy: Policy):
    """Restore 100% of the base Sum Insured."""

    if policy.restoration_used:
        raise ValueError(
            "Restoration has already been used"
        )

    policy.remaining_si = policy.sum_insured
    policy.restoration_used = True

    return policy.remaining_si


# =========================================================
# BR-10: NO-CLAIM BONUS
# =========================================================

def add_no_claim_bonus(policy: Policy):
    """Add 10% NCB for one claim-free year."""

    bonus_increment = policy.sum_insured * 0.10
    maximum_bonus = policy.sum_insured * 0.50

    policy.no_claim_bonus = min(
        policy.no_claim_bonus + bonus_increment,
        maximum_bonus
    )

    return policy.no_claim_bonus


def reduce_no_claim_bonus_at_renewal(
    policy: Policy
):
    """Reduce NCB by 10 percentage points."""

    reduction = policy.sum_insured * 0.10

    policy.no_claim_bonus = max(
        0,
        policy.no_claim_bonus - reduction
    )

    return policy.no_claim_bonus


# =========================================================
# BR-11: QUERY TIMELINE & RESUBMISSION
# =========================================================

def check_query_response_time(
    query_time,
    response_time
):
    """Check whether query was answered within 48 hours."""

    if response_time < query_time:
        raise ValueError(
            "Response time cannot be before query time"
        )

    time_difference = (
        response_time - query_time
    )

    # Exactly 48 hours is valid
    if time_difference <= timedelta(hours=48):
        return (
            True,
            "Query response received within 48 hours"
        )

    return (
        False,
        "REJECTED: Query response exceeded 48 hours"
    )


def can_resubmit_pre_auth(
    resubmission_count: int
):
    """A rejected pre-auth can be resubmitted once."""

    if resubmission_count < 0:
        raise ValueError(
            "Resubmission count cannot be negative"
        )

    return resubmission_count < 1
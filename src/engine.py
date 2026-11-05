from models import Policy, Member, Claim
from rules import (
    check_waiting_period,
    calculate_proportionate_factor,
    apply_proportionate_deduction,
    apply_disease_sub_limit,
    calculate_non_payable_deduction,
    calculate_copay_percentage,
    apply_copay
)


def process_claim(
    policy: Policy,
    member: Member,
    claim: Claim,
    actual_room_rent: float,
    hospital_zone: str,
    non_payable_amount: float = 0.0,
    consumable_cover: bool = False,
    accident_codes=None,
    specified_illnesses=None
):
    """
    Process a claim using the required business-rule precedence.
    """

    rule_ids = []

    # =====================================================
    # STEP 1: WAITING PERIOD
    # =====================================================

    eligible, message = check_waiting_period(
        policy,
        member,
        claim,
        accident_codes,
        specified_illnesses
    )

    if not eligible:
        claim.update_status("REJECTED")

        return {
            "status": "REJECTED",
            "message": message,
            "rule_ids": ["BR-01"]
        }

    rule_ids.append("BR-01")

    # Start with the estimated bill
    amount = claim.estimated_bill

    # =====================================================
    # STEP 2: ROOM PROPORTIONATE DEDUCTION
    # =====================================================

    factor, room_limit = calculate_proportionate_factor(
        policy,
        actual_room_rent
    )

    amount_after_room = apply_proportionate_deduction(
        amount,
        factor
    )

    room_deduction = amount - amount_after_room
    rule_ids.append("BR-02")

    # =====================================================
    # STEP 3: DISEASE SUB-LIMIT
    # =====================================================

    amount_after_sub_limit, sub_limit = apply_disease_sub_limit(
        policy,
        claim.diagnosis_code,
        amount_after_room
    )

    sub_limit_deduction = amount_after_room - amount_after_sub_limit
    rule_ids.append("BR-03")

    # =====================================================
    # STEP 4: NON-PAYABLES
    # =====================================================

    non_payable_deduction = calculate_non_payable_deduction(
        policy,
        amount_after_sub_limit,
        non_payable_amount,
        consumable_cover
    )

    amount_after_non_payables = max(
        0,
        amount_after_sub_limit - non_payable_deduction
    )

    rule_ids.append("BR-05")

    # =====================================================
    # STEP 5: CO-PAY
    # =====================================================

    copay_percentage = calculate_copay_percentage(
        policy,
        member,
        claim.admission_date,
        hospital_zone
    )

    customer_copay, insurance_payable_before_si = apply_copay(
        amount_after_non_payables,
        copay_percentage
    )

    rule_ids.append("BR-04")

    # =====================================================
    # STEP 6: SUM INSURED CAP
    # =====================================================

    insurance_payable = min(
        insurance_payable_before_si,
        policy.calculate_available_si()
    )

    si_deduction = (
        insurance_payable_before_si - insurance_payable
    )

    rule_ids.append("BR-07")

    # Determine claim status
    if insurance_payable <= 0:
        status = "REJECTED"
    elif insurance_payable < claim.estimated_bill:
        status = "PARTIAL"
    else:
        status = "APPROVED"

    claim.update_status(status)

    # Return the complete claim decision
    return {
        "status": status,
        "original_bill": claim.estimated_bill,
        "room_limit": room_limit,
        "room_deduction": room_deduction,
        "sub_limit": sub_limit,
        "sub_limit_deduction": sub_limit_deduction,
        "non_payable_deduction": non_payable_deduction,
        "copay_percentage": copay_percentage,
        "customer_copay": customer_copay,
        "si_deduction": si_deduction,
        "insurance_payable": insurance_payable,
        "rule_ids": rule_ids
    }
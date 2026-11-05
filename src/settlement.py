from src.validators import validate_positive_amount, validate_remaining_si


def calculate_final_settlement(
    final_bill,
    eligible_amount,
    remaining_si,
    initial_approved_amount,
    enhancement_approved_amount=0
):
    """
    Calculate FINAL_BILL settlement.
    """

    validate_positive_amount(final_bill, "Final bill")
    validate_positive_amount(eligible_amount, "Eligible amount")
    validate_remaining_si(remaining_si)

    if initial_approved_amount < 0:
        raise ValueError(
            "Initial approved amount cannot be negative."
        )

    if enhancement_approved_amount < 0:
        raise ValueError(
            "Enhancement approved amount cannot be negative."
        )

    total_authorized_amount = (
        initial_approved_amount + enhancement_approved_amount
    )

    insurance_payable = min(eligible_amount, remaining_si)

    customer_share = max(final_bill - insurance_payable, 0)

    released_amount = max(
        total_authorized_amount - insurance_payable,
        0
    )

    return {
        "status": "SETTLED",
        "final_bill": final_bill,
        "eligible_amount": eligible_amount,
        "remaining_si": remaining_si,
        "total_authorized_amount": total_authorized_amount,
        "insurance_payable": insurance_payable,
        "customer_share": customer_share,
        "released_amount": released_amount,
        "rule_id": "BR-07"
    }
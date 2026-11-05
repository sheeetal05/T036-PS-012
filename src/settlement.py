def calculate_final_settlement(
    final_bill,
    eligible_amount,
    remaining_si,
    initial_approved_amount,
    enhancement_approved_amount=0
):
    """
    Calculate FINAL_BILL settlement.

    BR-07:
    - Insurance payable is capped at remaining Sum Insured.
    - Customer pays the remaining balance.
    - If final payable is lower than the amount initially approved,
      the unused approved amount is released.
    """

    # Amount approved during pre-auth and enhancement
    total_authorized_amount = (
        initial_approved_amount + enhancement_approved_amount
    )

    # Insurance can pay only up to the eligible amount or remaining SI
    insurance_payable = min(eligible_amount, remaining_si)

    # Customer pays the balance of the final bill
    customer_share = max(final_bill - insurance_payable, 0)

    # Release unused authorised amount
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
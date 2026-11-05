def calculate_initial_approval(eligible_amount, remaining_si):
    """
    Calculate the initial PRE_AUTH approval amount.

    BR-06:
    Initial approval is the minimum of:
    - Eligible estimated bill
    - 60% of remaining Sum Insured
    - Rs. 2,00,000
    """

    sixty_percent_si = remaining_si * 0.60
    maximum_initial_approval = 200000

    approved_amount = min(
        eligible_amount,
        sixty_percent_si,
        maximum_initial_approval
    )

    return {
        "eligible_amount": eligible_amount,
        "remaining_si": remaining_si,
        "si_limit_60_percent": sixty_percent_si,
        "maximum_initial_approval": maximum_initial_approval,
        "approved_amount": approved_amount,
        "rule_id": "BR-06"
    }
from datetime import datetime, date


def calculate_enhancement(
    requested_amount,
    remaining_si,
    request_datetime,
    discharge_date
):
    """
    Calculate whether an enhancement request is allowed.

    BR-06:
    - Enhancement can be approved up to the remaining Sum Insured.
    - Enhancement request must arrive before the discharge date.
    """

    # Convert datetime to date if needed
    if isinstance(request_datetime, datetime):
        request_date = request_datetime.date()
    else:
        request_date = request_datetime

    # Check if enhancement arrived after discharge
    if request_date > discharge_date:
        return {
            "status": "REJECTED",
            "approved_amount": 0,
            "reason": "Enhancement request received after discharge date",
            "rule_id": "BR-06"
        }

    # Approve only up to remaining Sum Insured
    approved_amount = min(requested_amount, remaining_si)

    status = "APPROVED" if approved_amount == requested_amount else "PARTIAL"

    return {
        "status": status,
        "requested_amount": requested_amount,
        "remaining_si": remaining_si,
        "approved_amount": approved_amount,
        "rule_id": "BR-06"
    }
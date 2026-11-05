from datetime import datetime
from src.validators import validate_positive_amount, validate_remaining_si


def calculate_enhancement(
    requested_amount,
    remaining_si,
    request_datetime,
    discharge_date
):
    """
    Calculate whether an enhancement request is allowed.
    """

    validate_positive_amount(requested_amount, "Requested amount")
    validate_remaining_si(remaining_si)

    # Convert datetime to date
    if isinstance(request_datetime, datetime):
        request_date = request_datetime.date()
    else:
        request_date = request_datetime

    # Request after discharge is rejected
    if request_date > discharge_date:
        return {
            "status": "REJECTED",
            "requested_amount": requested_amount,
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
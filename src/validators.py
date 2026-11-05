def validate_positive_amount(amount, field_name):
    """
    Validates that an amount is greater than zero.
    """

    if amount <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return True


def validate_remaining_si(remaining_si):
    """
    Validates that remaining Sum Insured is not negative.
    """

    if remaining_si < 0:
        raise ValueError(
            "Remaining Sum Insured cannot be negative."
        )

    return True


def validate_command(command_type, values, expected_values):
    """
    Validates the number of values in a command.
    """

    if len(values) < expected_values:
        raise ValueError(
            f"{command_type} requires at least "
            f"{expected_values} values."
        )

    return True
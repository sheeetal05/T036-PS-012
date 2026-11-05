def handle_command(command):
    """
    Handles one parsed command.

    Returns a message describing the action taken.
    """

    command_type = command["command_type"]
    values = command["values"]

    if command_type == "REGISTER_POLICY":
        return {
            "status": "SUCCESS",
            "action": "REGISTER_POLICY",
            "message": f"Policy registration command received: {values}"
        }

    elif command_type == "PRE_AUTH":
        return {
            "status": "SUCCESS",
            "action": "PRE_AUTH",
            "message": f"Pre-authorisation command received: {values}"
        }

    elif command_type == "ENHANCEMENT":
        return {
            "status": "SUCCESS",
            "action": "ENHANCEMENT",
            "message": f"Enhancement command received: {values}"
        }

    elif command_type == "FINAL_BILL":
        return {
            "status": "SUCCESS",
            "action": "FINAL_BILL",
            "message": f"Final bill command received: {values}"
        }

    else:
        return {
            "status": "ERROR",
            "action": command_type,
            "message": f"Unknown command: {command_type}"
        }


def handle_all_commands(parsed_commands):
    """
    Handles all parsed commands.
    """

    results = []

    for command in parsed_commands:
        result = handle_command(command)
        results.append(result)

    return results
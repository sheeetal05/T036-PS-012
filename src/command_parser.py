def parse_command(command):
    """
    Separates one command into its command type and values.
    """

    parts = command.split()

    if not parts:
        return None

    return {
        "command_type": parts[0],
        "values": parts[1:]
    }


def parse_all_commands(commands):
    """
    Parses all commands from the command file.
    """

    parsed_commands = []

    for command in commands:
        parsed = parse_command(command)

        if parsed:
            parsed_commands.append(parsed)

    return parsed_commands
def read_commands(file_path):
    """
    Reads commands from a text file.
    Ignores empty lines and comments starting with #.
    """

    commands = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                command = line.strip()

                if not command:
                    continue

                if command.startswith("#"):
                    continue

                commands.append(command)

    except FileNotFoundError:
        print(f"\nCommand file not found: {file_path}")

    return commands


def display_commands(commands):
    """Displays all commands."""

    if not commands:
        print("No commands found.")
        return

    print("\n===== COMMANDS =====")

    for number, command in enumerate(commands, start=1):
        print(f"{number}. {command}")
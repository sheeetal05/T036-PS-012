from datetime import date, datetime
from pathlib import Path

from src.models import Member, Policy, Claim
from src.engine import process_claim
from src.command_processor import read_commands, display_commands
from src.command_parser import parse_all_commands
from src.command_handler import handle_all_commands
from src.store import DataStore
from src.preauth import calculate_initial_approval
from src.enhancement import calculate_enhancement
from src.settlement import calculate_final_settlement


def save_results(results, output_file):
    """
    Saves command processing results in a clean,
    readable format.
    """

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:

        file.write("=" * 60 + "\n")
        file.write("HEALTH INSURANCE CLAIM PROCESSING RESULTS\n")
        file.write("=" * 60 + "\n\n")

        for index, result in enumerate(results, start=1):

            action = result.get("action", "UNKNOWN")
            status = result.get("status", "UNKNOWN")

            file.write("=" * 60 + "\n")
            file.write(f"RESULT {index}: {action}\n")
            file.write("=" * 60 + "\n")

            file.write(f"Status: {status}\n")

            # Basic details
            if "policy_id" in result:
                file.write(f"Policy ID: {result['policy_id']}\n")

            if "member_id" in result:
                file.write(f"Member ID: {result['member_id']}\n")

            if "claim_id" in result:
                file.write(f"Claim ID: {result['claim_id']}\n")

            if "message" in result:
                file.write(f"Message: {result['message']}\n")

            # PRE_AUTH details
            if "preauth_result" in result:

                preauth = result["preauth_result"]

                file.write("\nPRE-AUTH DETAILS\n")
                file.write("-" * 40 + "\n")

                file.write(
                    f"Eligible Amount: ₹{preauth.get('eligible_amount', 0)}\n"
                )

                file.write(
                    f"Approved Amount: ₹{preauth.get('approved_amount', 0)}\n"
                )

                file.write(
                    f"Remaining SI: ₹{preauth.get('remaining_si', 0)}\n"
                )

                file.write(
                    f"Rule ID: {preauth.get('rule_id', 'N/A')}\n"
                )

            # ENHANCEMENT details
            if "enhancement_result" in result:

                enhancement = result["enhancement_result"]

                file.write("\nENHANCEMENT DETAILS\n")
                file.write("-" * 40 + "\n")

                file.write(
                    f"Requested Amount: ₹{enhancement.get('requested_amount', 0)}\n"
                )

                file.write(
                    f"Approved Amount: ₹{enhancement.get('approved_amount', 0)}\n"
                )

                file.write(
                    f"Remaining SI: ₹{enhancement.get('remaining_si', 0)}\n"
                )

                file.write(
                    f"Rule ID: {enhancement.get('rule_id', 'N/A')}\n"
                )

            # FINAL BILL details
            if "settlement_result" in result:

                settlement = result["settlement_result"]

                file.write("\nFINAL SETTLEMENT DETAILS\n")
                file.write("-" * 40 + "\n")

                file.write(
                    f"Final Bill: ₹{settlement.get('final_bill', 0)}\n"
                )

                file.write(
                    f"Insurance Payable: ₹{settlement.get('insurance_payable', 0)}\n"
                )

                file.write(
                    f"Customer Share: ₹{settlement.get('customer_share', 0)}\n"
                )

                file.write(
                    f"Rule ID: {settlement.get('rule_id', 'N/A')}\n"
                )

            file.write("\n\n")


def main():

    # =============================================
    # PROJECT PATHS
    # =============================================

    project_folder = Path(__file__).resolve().parent.parent

    command_file = (
        project_folder / "data" / "input" / "commands.txt"
    )

    output_file = (
        project_folder / "data" / "output" / "results.txt"
    )

    # =============================================
    # READ COMMAND FILE
    # =============================================

    print("\n===== COMMANDS =====")

    commands = read_commands(command_file)

    display_commands(commands)

    # =============================================
    # PARSE COMMANDS
    # =============================================

    parsed_commands = parse_all_commands(commands)

    print("\n===== PARSED COMMANDS =====")

    for command in parsed_commands:
        print(command)

    # =============================================
    # CREATE DATA STORE
    # =============================================

    store = DataStore()

    # =============================================
    # PROCESS ALL COMMANDS
    # =============================================

    command_results = handle_all_commands(
        parsed_commands,
        store
    )

    # =============================================
    # DISPLAY RESULTS
    # =============================================

    print("\n===== COMMAND RESULTS =====")

    for result in command_results:
        print(result)

    # =============================================
    # SAVE RESULTS TO FILE
    # =============================================

    save_results(command_results, output_file)

    print("\nResults saved successfully!")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
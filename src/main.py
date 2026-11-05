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


def main():

    # =============================================
    # TEMPORARY TEST MEMBER
    # =============================================

    member = Member(
        member_id="M001",
        name="Test Member",
        date_of_birth=date(1960, 1, 1)
    )

    # =============================================
    # TEMPORARY TEST POLICY
    # =============================================

    policy = Policy(
        policy_id="P001",
        sum_insured=500000,
        plan="SILVER",
        inception_date=date(2026, 1, 1),
        zone="A",
        members=[member]
    )

    # =============================================
    # TEMPORARY TEST CLAIM
    # =============================================

    claim = Claim(
        claim_id="C001",
        policy_id="P001",
        member_id="M001",
        diagnosis_code="HERNIA",
        icd_chapter="K",
        estimated_bill=150000,
        admission_date=date(2026, 3, 15)
    )

    # =============================================
    # PROCESS CLAIM
    # =============================================

    decision = process_claim(
        policy=policy,
        member=member,
        claim=claim,
        actual_room_rent=8000,
        hospital_zone="C",
        non_payable_amount=5000,
        consumable_cover=False,
        accident_codes=[],
        specified_illnesses=[]
    )

    # =============================================
    # DISPLAY CLAIM DECISION
    # =============================================

    print("\n===== CLAIM DECISION =====")

    for key, value in decision.items():
        print(f"{key}: {value}")

    # =============================================
    # PRE-AUTH INITIAL APPROVAL
    # =============================================

    preauth_result = calculate_initial_approval(
        eligible_amount=decision["insurance_payable"],
        remaining_si=policy.sum_insured
    )

    print("\n===== PRE-AUTH INITIAL APPROVAL =====")

    for key, value in preauth_result.items():
        print(f"{key}: {value}")

    # =============================================
    # ENHANCEMENT TEST
    # =============================================

    enhancement_result = calculate_enhancement(
        requested_amount=50000,
        remaining_si=policy.sum_insured - preauth_result["approved_amount"],
        request_datetime=datetime(2026, 3, 16, 10, 30),
        discharge_date=date(2026, 3, 20)
    )

    print("\n===== ENHANCEMENT RESULT =====")

    for key, value in enhancement_result.items():
        print(f"{key}: {value}")

    # =============================================
    # FINAL BILL SETTLEMENT TEST
    # =============================================

    final_settlement = calculate_final_settlement(
        final_bill=140000,
        eligible_amount=decision["insurance_payable"],
        remaining_si=policy.sum_insured,
        initial_approved_amount=preauth_result["approved_amount"],
        enhancement_approved_amount=enhancement_result["approved_amount"]
    )

    print("\n===== FINAL BILL SETTLEMENT =====")

    for key, value in final_settlement.items():
        print(f"{key}: {value}")

    # =============================================
    # READ COMMAND FILE
    # =============================================

    project_folder = Path(__file__).resolve().parent.parent
    command_file = project_folder / "data" / "input" / "commands.txt"

    print(f"\nLooking for command file at:\n{command_file}")

    # Read commands
    commands = read_commands(command_file)

    # Display original commands
    display_commands(commands)

    # Parse commands
    parsed_commands = parse_all_commands(commands)

    # =============================================
    # DISPLAY PARSED COMMANDS
    # =============================================

    print("\n===== PARSED COMMANDS =====")

    for command in parsed_commands:
        print(command)

    # =============================================
    # CREATE DATA STORE AND HANDLE COMMANDS
    # =============================================

    store = DataStore()

    command_results = handle_all_commands(
        parsed_commands,
        store
    )

    print("\n===== COMMAND RESULTS =====")

    for result in command_results:
        print(result)


if __name__ == "__main__":
    main()
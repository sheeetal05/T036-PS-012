from datetime import date
from pathlib import Path

from src.models import Member, Policy, Claim
from src.engine import process_claim
from src.command_processor import read_commands, display_commands
from src.command_parser import parse_all_commands


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
    # READ AND PARSE COMMAND FILE
    # =============================================

    project_folder = Path(__file__).resolve().parent.parent

    # Updated to use input folder
    command_file = project_folder / "data" / "input" / "commands.txt"

    print(f"\nLooking for command file at:\n{command_file}")

    commands = read_commands(command_file)

    display_commands(commands)

    parsed_commands = parse_all_commands(commands)

    print("\n===== PARSED COMMANDS =====")

    for command in parsed_commands:
        print(command)


if __name__ == "__main__":
    main()
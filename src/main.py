from datetime import date

from models import Member, Policy, Claim
from engine import process_claim


# Create member
member = Member(
    member_id="M001",
    name="Test Member",
    date_of_birth=date(1960, 5, 10)
)

# Create policy
policy = Policy(
    policy_id="P001",
    sum_insured=500000,
    plan="SILVER",
    inception_date=date(2025, 1, 1),
    zone="A",
    members=[member]
)

# Create claim
claim = Claim(
    claim_id="C001",
    policy_id="P001",
    member_id="M001",
    diagnosis_code="HERNIA",
    icd_chapter="K",
    admission_date=date(2026, 10, 1),
    estimated_bill=150000
)

# Process claim
result = process_claim(
    policy=policy,
    member=member,
    claim=claim,
    actual_room_rent=8000,
    hospital_zone="C",
    non_payable_amount=5000,
    consumable_cover=False,
    specified_illnesses=[]
)

print("\n===== CLAIM DECISION =====")

for key, value in result.items():
    print(f"{key}: {value}")
from datetime import date, datetime, timedelta

from src.models import Member, Policy
from src.rules import (
    calculate_age_on_date,
    calculate_pre_auth_approval,
    check_query_response_time,
    can_resubmit_pre_auth,
    calculate_proportionate_factor,
    apply_disease_sub_limit,
    calculate_non_payable_deduction
)


# =========================================================
# TEST 1: MEMBER TURNING 61 ON ADMISSION DATE
# =========================================================

def test_age_61_on_admission_date():
    birth_date = date(1965, 10, 1)
    admission_date = date(2026, 10, 1)

    age = calculate_age_on_date(
        birth_date,
        admission_date
    )

    assert age == 61


# =========================================================
# TEST 2: PRE-AUTH MAXIMUM CAP
# =========================================================

def test_pre_auth_maximum_cap():
    approval = calculate_pre_auth_approval(
        eligible_estimated_bill=500000,
        remaining_si=500000
    )

    assert approval == 200000


# =========================================================
# TEST 3: QUERY RESPONSE EXACTLY AT 48 HOURS
# =========================================================

def test_query_response_exactly_48_hours():
    query_time = datetime(2026, 10, 1, 10, 0)

    response_time = query_time + timedelta(hours=48)

    valid, message = check_query_response_time(
        query_time,
        response_time
    )

    assert valid is True


# =========================================================
# TEST 4: ONLY ONE RESUBMISSION ALLOWED
# =========================================================

def test_only_one_resubmission_allowed():

    # First resubmission is allowed
    assert can_resubmit_pre_auth(0) is True

    # Second resubmission is not allowed
    assert can_resubmit_pre_auth(1) is False


# =========================================================
# TEST 5: ROOM RENT EXACTLY AT LIMIT
# =========================================================

def test_room_rent_exactly_at_limit():

    member = Member(
        member_id="M001",
        name="Test Member",
        date_of_birth=date(2000, 1, 1)
    )

    policy = Policy(
        policy_id="P001",
        sum_insured=500000,
        plan="SILVER",
        inception_date=date(2026, 1, 1),
        zone="A",
        members=[member]
    )

    factor, room_limit = calculate_proportionate_factor(
        policy,
        actual_room_rent=5000
    )

    assert room_limit == 5000
    assert factor == 1


# =========================================================
# TEST 6: DISEASE SUB-LIMIT
# =========================================================

def test_disease_sub_limit_applied_after_room_deduction():

    member = Member(
        member_id="M001",
        name="Test Member",
        date_of_birth=date(2000, 1, 1)
    )

    policy = Policy(
        policy_id="P002",
        sum_insured=500000,
        plan="SILVER",
        inception_date=date(2026, 1, 1),
        zone="A",
        members=[member]
    )

    # Amount after room proportionate deduction
    amount_after_room = 80000

    eligible_amount, sub_limit = apply_disease_sub_limit(
        policy,
        "HERNIA",
        amount_after_room
    )

    assert sub_limit == 60000
    assert eligible_amount == 60000


# =========================================================
# TEST 7: PLATINUM NON-PAYABLE CAP
# =========================================================

def test_platinum_non_payable_cap():

    member = Member(
        member_id="M001",
        name="Test Member",
        date_of_birth=date(2000, 1, 1)
    )

    policy = Policy(
        policy_id="P003",
        sum_insured=500000,
        plan="PLATINUM",
        inception_date=date(2026, 1, 1),
        zone="A",
        members=[member]
    )

    deduction = calculate_non_payable_deduction(
        policy,
        total_bill=100000,
        non_payable_amount=15000,
        consumable_cover=False
    )

    # 10% of ₹1,00,000 = ₹10,000
    assert deduction == 10000
from datetime import date, datetime

from src.preauth import calculate_initial_approval
from src.enhancement import calculate_enhancement
from src.settlement import calculate_final_settlement


# =============================================
# PRE-AUTH TESTS
# =============================================

def test_preauth_uses_eligible_amount_when_lowest():
    result = calculate_initial_approval(
        eligible_amount=50000,
        remaining_si=500000
    )

    assert result["approved_amount"] == 50000
    assert result["rule_id"] == "BR-06"


def test_preauth_caps_at_200000():
    result = calculate_initial_approval(
        eligible_amount=400000,
        remaining_si=1000000
    )

    assert result["approved_amount"] == 200000


def test_preauth_respects_si_percentage_limit():
    result = calculate_initial_approval(
        eligible_amount=300000,
        remaining_si=200000
    )

    # 60% of 2,00,000 = 1,20,000
    assert result["approved_amount"] == 120000


# =============================================
# ENHANCEMENT TESTS
# =============================================

def test_enhancement_approved_before_discharge():
    result = calculate_enhancement(
        requested_amount=50000,
        remaining_si=100000,
        request_datetime=datetime(2026, 3, 16, 10, 0),
        discharge_date=date(2026, 3, 20)
    )

    assert result["status"] == "APPROVED"
    assert result["approved_amount"] == 50000


def test_enhancement_rejected_after_discharge():
    result = calculate_enhancement(
        requested_amount=50000,
        remaining_si=100000,
        request_datetime=datetime(2026, 3, 21, 10, 0),
        discharge_date=date(2026, 3, 20)
    )

    assert result["status"] == "REJECTED"
    assert result["approved_amount"] == 0


def test_enhancement_partial_when_si_is_low():
    result = calculate_enhancement(
        requested_amount=100000,
        remaining_si=40000,
        request_datetime=datetime(2026, 3, 16, 10, 0),
        discharge_date=date(2026, 3, 20)
    )

    assert result["status"] == "PARTIAL"
    assert result["approved_amount"] == 40000


# =============================================
# FINAL SETTLEMENT TESTS
# =============================================

def test_final_settlement_normal_case():
    result = calculate_final_settlement(
        final_bill=140000,
        eligible_amount=100000,
        remaining_si=200000,
        initial_approved_amount=80000,
        enhancement_approved_amount=20000
    )

    assert result["status"] == "SETTLED"
    assert result["insurance_payable"] == 100000
    assert result["customer_share"] == 40000


def test_final_settlement_caps_at_remaining_si():
    result = calculate_final_settlement(
        final_bill=300000,
        eligible_amount=250000,
        remaining_si=150000,
        initial_approved_amount=100000,
        enhancement_approved_amount=50000
    )

    assert result["insurance_payable"] == 150000
    assert result["customer_share"] == 150000


def test_final_settlement_releases_unused_amount():
    result = calculate_final_settlement(
        final_bill=50000,
        eligible_amount=50000,
        remaining_si=200000,
        initial_approved_amount=100000,
        enhancement_approved_amount=50000
    )

    assert result["released_amount"] == 100000
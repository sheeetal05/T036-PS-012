from datetime import date, datetime, timedelta

from src.models import Member, Policy, Claim
from src.engine import process_claim
from src.preauth import calculate_initial_approval
from src.enhancement import calculate_enhancement
from src.settlement import calculate_final_settlement


def handle_command(command, store):
    """
    Handles one parsed command and performs the required action.
    """

    command_type = command["command_type"]
    values = command["values"]

    # =============================================
    # REGISTER POLICY
    # Format: REGISTER_POLICY policy_id plan sum_insured
    # =============================================

    if command_type == "REGISTER_POLICY":

        if len(values) < 3:
            return {
                "status": "ERROR",
                "action": "REGISTER_POLICY",
                "message": "Invalid REGISTER_POLICY command."
            }

        policy_id = values[0]
        plan = values[1]

        try:
            sum_insured = float(values[2])
        except ValueError:
            return {
                "status": "ERROR",
                "action": "REGISTER_POLICY",
                "message": "Sum insured must be a number."
            }

        if sum_insured <= 0:
            return {
                "status": "ERROR",
                "action": "REGISTER_POLICY",
                "message": "Sum insured must be greater than zero."
            }

        policy = Policy(
            policy_id=policy_id,
            sum_insured=sum_insured,
            plan=plan,
            inception_date=date.today() - timedelta(days=60),
            zone="A",
            members=[]
        )

        store.add_policy(policy)

        return {
            "status": "SUCCESS",
            "action": "REGISTER_POLICY",
            "policy_id": policy_id,
            "message": f"Policy {policy_id} registered successfully."
        }

    # =============================================
    # PRE_AUTH
    # Format: PRE_AUTH policy_id member_id diagnosis estimated_bill
    # =============================================

    elif command_type == "PRE_AUTH":

        if len(values) < 4:
            return {
                "status": "ERROR",
                "action": "PRE_AUTH",
                "message": "Invalid PRE_AUTH command."
            }

        policy_id = values[0]
        member_id = values[1]
        diagnosis = values[2]

        try:
            estimated_bill = float(values[3])
        except ValueError:
            return {
                "status": "ERROR",
                "action": "PRE_AUTH",
                "message": "Estimated bill must be a number."
            }

        if estimated_bill <= 0:
            return {
                "status": "ERROR",
                "action": "PRE_AUTH",
                "message": "Estimated bill must be greater than zero."
            }

        policy = store.get_policy(policy_id)

        if policy is None:
            return {
                "status": "ERROR",
                "action": "PRE_AUTH",
                "message": f"Policy {policy_id} not found."
            }

        member = store.get_member(member_id)

        if member is None:
            member = Member(
                member_id=member_id,
                name=f"Member {member_id}",
                date_of_birth=date(1980, 1, 1)
            )
            store.add_member(member)
            policy.members.append(member)

        claim_id = f"C{len(store.claims) + 1:03d}"

        claim = Claim(
            claim_id=claim_id,
            policy_id=policy_id,
            member_id=member_id,
            diagnosis_code=diagnosis,
            icd_chapter="K",
            estimated_bill=estimated_bill,
            admission_date=date.today()
        )

        store.add_claim(claim)

        decision = process_claim(
            policy=policy,
            member=member,
            claim=claim,
            actual_room_rent=0,
            hospital_zone=policy.zone,
            non_payable_amount=0,
            consumable_cover=True,
            accident_codes=[],
            specified_illnesses=[]
        )

        if "insurance_payable" not in decision:
            return {
                "status": "ERROR",
                "action": "PRE_AUTH",
                "claim_id": claim_id,
                "message": "Claim could not be processed by the claim engine.",
                "claim_decision": decision
            }

        preauth_result = calculate_initial_approval(
            eligible_amount=decision["insurance_payable"],
            remaining_si=policy.sum_insured
        )

        store.save_preauth(claim_id, preauth_result)

        return {
            "status": "SUCCESS",
            "action": "PRE_AUTH",
            "claim_id": claim_id,
            "policy_id": policy_id,
            "member_id": member_id,
            "claim_decision": decision,
            "preauth_result": preauth_result
        }

    # =============================================
    # ENHANCEMENT
    # Format: ENHANCEMENT claim_id requested_amount
    # =============================================

    elif command_type == "ENHANCEMENT":

        if len(values) < 2:
            return {
                "status": "ERROR",
                "action": "ENHANCEMENT",
                "message": "Invalid ENHANCEMENT command."
            }

        claim_id = values[0]

        try:
            requested_amount = float(values[1])
        except ValueError:
            return {
                "status": "ERROR",
                "action": "ENHANCEMENT",
                "message": "Requested amount must be a number."
            }

        if requested_amount <= 0:
            return {
                "status": "ERROR",
                "action": "ENHANCEMENT",
                "message": "Requested amount must be greater than zero."
            }

        claim = store.get_claim(claim_id)
        preauth = store.get_preauth(claim_id)

        if claim is None:
            return {
                "status": "ERROR",
                "action": "ENHANCEMENT",
                "message": f"Claim {claim_id} not found."
            }

        if preauth is None:
            return {
                "status": "ERROR",
                "action": "ENHANCEMENT",
                "message": f"No PRE_AUTH found for claim {claim_id}."
            }

        policy = store.get_policy(claim.policy_id)

        remaining_si = (
            policy.sum_insured - preauth["approved_amount"]
        )

        enhancement_result = calculate_enhancement(
            requested_amount=requested_amount,
            remaining_si=remaining_si,
            request_datetime=datetime.now(),
            discharge_date=date.today() + timedelta(days=7)
        )

        store.save_enhancement(claim_id, enhancement_result)

        return {
            "status": enhancement_result["status"],
            "action": "ENHANCEMENT",
            "claim_id": claim_id,
            "requested_amount": requested_amount,
            "enhancement_result": enhancement_result
        }

    # =============================================
    # FINAL BILL
    # Format: FINAL_BILL claim_id final_bill_amount
    # =============================================

    elif command_type == "FINAL_BILL":

        if len(values) < 2:
            return {
                "status": "ERROR",
                "action": "FINAL_BILL",
                "message": "Invalid FINAL_BILL command."
            }

        claim_id = values[0]

        try:
            final_bill = float(values[1])
        except ValueError:
            return {
                "status": "ERROR",
                "action": "FINAL_BILL",
                "message": "Final bill must be a number."
            }

        if final_bill <= 0:
            return {
                "status": "ERROR",
                "action": "FINAL_BILL",
                "message": "Final bill must be greater than zero."
            }

        # Find all required data
        claim = store.get_claim(claim_id)
        preauth = store.get_preauth(claim_id)
        enhancement = store.get_enhancement(claim_id)

        if claim is None:
            return {
                "status": "ERROR",
                "action": "FINAL_BILL",
                "message": f"Claim {claim_id} not found."
            }

        if preauth is None:
            return {
                "status": "ERROR",
                "action": "FINAL_BILL",
                "message": f"No PRE_AUTH found for claim {claim_id}."
            }

        policy = store.get_policy(claim.policy_id)

        # Get enhancement amount if available
        enhancement_amount = 0

        if enhancement is not None:
            enhancement_amount = enhancement.get(
                "approved_amount",
                0
            )

        # Remaining SI after approvals
        remaining_si = (
            policy.sum_insured
            - preauth["approved_amount"]
            - enhancement_amount
        )

        # Use the original claim engine decision
        # as the eligible amount for final settlement.
        eligible_amount = min(
            final_bill,
            claim.estimated_bill
        )

        settlement_result = calculate_final_settlement(
            final_bill=final_bill,
            eligible_amount=eligible_amount,
            remaining_si=remaining_si,
            initial_approved_amount=preauth["approved_amount"],
            enhancement_approved_amount=enhancement_amount
        )

        return {
            "status": settlement_result["status"],
            "action": "FINAL_BILL",
            "claim_id": claim_id,
            "settlement_result": settlement_result
        }

    # =============================================
    # UNKNOWN COMMAND
    # =============================================

    return {
        "status": "ERROR",
        "action": command_type,
        "message": f"Unknown command: {command_type}"
    }


def handle_all_commands(parsed_commands, store):
    """
    Handles all commands using the same DataStore.
    """

    results = []

    for command in parsed_commands:
        result = handle_command(command, store)
        results.append(result)

    return results
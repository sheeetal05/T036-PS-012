classDiagram

    class Policy {
        +String policy_id
        +float sum_insured
        +String plan
        +Date inception_date
        +String zone
        +float remaining_si
        +float no_claim_bonus
        +bool restoration_used

        +calculate_available_si()
        +consume_si()
        +restore_si()
    }

    class Member {
        +String member_id
        +String name
        +Date date_of_birth
        +List ped_list

        +is_ped()
    }

    class Claim {
        +String claim_id
        +String policy_id
        +String member_id
        +String diagnosis_code
        +String icd_chapter
        +Date admission_date
        +Date discharge_date
        +String room_category
        +float estimated_bill
        +String status

        +update_status()
    }

    class PreAuthorisation {
        +String request_id
        +String claim_id
        +float requested_amount
        +float approved_amount
        +String decision
        +List rule_ids

        +calculate_approval()
    }

    class Enhancement {
        +String enhancement_id
        +String claim_id
        +float requested_amount
        +DateTime request_timestamp
        +float approved_amount

        +validate_request()
    }

    class FinalSettlement {
        +String claim_id
        +float final_bill
        +float eligible_amount
        +float co_pay_amount
        +float insurance_payable
        +float customer_share

        +calculate_payable()
    }

    class Hospital {
        +String hospital_id
        +String name
        +String zone
        +bool network_status

        +get_tariff()
    }

    Policy "1" --> "*" Member : covers
    Policy "1" --> "*" Claim : has
    Claim "1" --> "1" PreAuthorisation : has
    Claim "1" --> "*" Enhancement : may have
    Claim "1" --> "1" FinalSettlement : settled by
    Claim --> Hospital : processed at
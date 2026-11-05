stateDiagram-v2

    [*] --> PRE_AUTH_RECEIVED

    PRE_AUTH_RECEIVED --> UNDER_REVIEW : Start validation

    UNDER_REVIEW --> REJECTED : Waiting period or validation failed
    UNDER_REVIEW --> QUERY : Additional information required
    UNDER_REVIEW --> APPROVED : Fully approved
    UNDER_REVIEW --> PARTIAL : Partially approved

    QUERY --> UNDER_REVIEW : Response within 48 hours
    QUERY --> REJECTED : No response within 48 hours

    APPROVED --> ENHANCEMENT_PENDING : Enhancement requested
    PARTIAL --> ENHANCEMENT_PENDING : Enhancement requested

    ENHANCEMENT_PENDING --> APPROVED : Valid request before discharge
    ENHANCEMENT_PENDING --> PARTIAL : Partially approved
    ENHANCEMENT_PENDING --> REJECTED : Request after discharge

    APPROVED --> FINAL_BILL_RECEIVED : Final bill submitted
    PARTIAL --> FINAL_BILL_RECEIVED : Final bill submitted

    FINAL_BILL_RECEIVED --> SETTLED : Calculate final settlement

    REJECTED --> PRE_AUTH_RECEIVED : Resubmission allowed once

    SETTLED --> [*]
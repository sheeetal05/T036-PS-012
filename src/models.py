from dataclasses import dataclass, field
from datetime import date


@dataclass
class Member:
    member_id: str
    name: str
    date_of_birth: date
    ped_list: list[str] = field(default_factory=list)


@dataclass
class Policy:
    policy_id: str
    sum_insured: float
    plan: str
    inception_date: date
    zone: str
    members: list[Member] = field(default_factory=list)

    remaining_si: float = field(init=False)
    no_claim_bonus: float = 0.0
    restoration_used: bool = False

    def __post_init__(self):
        # Initially, the remaining Sum Insured is the full Sum Insured
        self.remaining_si = self.sum_insured

    def calculate_available_si(self):
        """Return the currently available Sum Insured."""
        return self.remaining_si + self.no_claim_bonus

    def consume_si(self, amount):
        """Consume the available Sum Insured."""

        if amount > self.calculate_available_si():
            raise ValueError("Amount exceeds available Sum Insured")

        # BR-10: Consume No-Claim Bonus before the base Sum Insured
        bonus_used = min(amount, self.no_claim_bonus)
        self.no_claim_bonus -= bonus_used

        remaining_amount = amount - bonus_used
        self.remaining_si -= remaining_amount


@dataclass
class Claim:
    claim_id: str
    policy_id: str
    member_id: str
    diagnosis_code: str
    icd_chapter: str
    admission_date: date
    discharge_date: date | None = None
    room_category: str = ""
    estimated_bill: float = 0.0
    status: str = "PRE_AUTH_RECEIVED"

    def update_status(self, new_status):
        """Update the current status of the claim."""
        self.status = new_status
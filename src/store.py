class DataStore:
    """
    Temporary in-memory storage for the insurance engine.
    """

    def __init__(self):
        self.policies = {}
        self.members = {}
        self.claims = {}
        self.preauth_approvals = {}
        self.enhancements = {}

    # =============================================
    # POLICY
    # =============================================

    def add_policy(self, policy):
        self.policies[policy.policy_id] = policy

    def get_policy(self, policy_id):
        return self.policies.get(policy_id)

    # =============================================
    # MEMBER
    # =============================================

    def add_member(self, member):
        self.members[member.member_id] = member

    def get_member(self, member_id):
        return self.members.get(member_id)

    # =============================================
    # CLAIM
    # =============================================

    def add_claim(self, claim):
        self.claims[claim.claim_id] = claim

    def get_claim(self, claim_id):
        return self.claims.get(claim_id)

    # =============================================
    # PRE-AUTH APPROVAL
    # =============================================

    def save_preauth(self, claim_id, result):
        self.preauth_approvals[claim_id] = result

    def get_preauth(self, claim_id):
        return self.preauth_approvals.get(claim_id)

    # =============================================
    # ENHANCEMENT
    # =============================================

    def save_enhancement(self, claim_id, result):
        self.enhancements[claim_id] = result

    def get_enhancement(self, claim_id):
        return self.enhancements.get(claim_id)
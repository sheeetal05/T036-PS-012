# T036 – PS-012

## Health Insurance Cashless Pre-Authorisation and Settlement Engine

### Business Rule Register

| Rule ID | Rule Name | Summary |
|---|---|---|
| BR-01 | Waiting Period | Check whether the policy waiting period has been completed before processing a claim. |
| BR-02 | Room Rent Limit | Apply plan-based room rent limits and proportionate deductions. |
| BR-03 | Disease Sub-limits | Apply maximum coverage limits for specified diseases and procedures. |
| BR-04 | Co-pay | Calculate customer contribution based on age and hospital zone. |
| BR-05 | Non-payables | Deduct expenses that are not covered by the policy. |
| BR-06 | Pre-authorisation & Enhancement | Calculate initial approval and process additional enhancement requests. |
| BR-07 | Final Bill Settlement | Calculate the final insurer payment and customer share. |
| BR-08 | Pre/Post-Hospitalisation | Process eligible expenses before and after hospitalisation. |
| BR-09 | Sum Insured Restoration | Restore exhausted sum insured for eligible unrelated illnesses. |
| BR-10 | No-Claim Bonus | Manage additional sum insured earned during claim-free years. |
| BR-11 | Query Timeline | Handle query responses within the 48-hour deadline and resubmissions. |
| BR-12 | Deduction Precedence | Apply all deductions in the required order. |
## BR-01 – Waiting Period

### Purpose
To determine whether a health insurance claim is eligible based on the time elapsed between the policy inception date and the member's admission date.

### Rules

1. A normal illness is subject to an initial waiting period of 30 days from the policy inception date.
2. Claims with accident diagnosis codes are exempt from the initial 30-day waiting period.
3. Listed specified illnesses are subject to a waiting period of 24 months.
4. A pre-existing disease (PED) is subject to a waiting period of 36 months.
5. If a claim falls within an applicable waiting period, the claim must be rejected with the relevant waiting-period rule ID.

### Inputs Required

- Policy inception date
- Admission date
- Diagnosis code
- Member's pre-existing disease (PED) list
- Specified illness list

### Expected Outcome

| Condition | Result |
|---|---|
| Waiting period completed | Continue processing the claim |
| Claim is within waiting period | REJECTED |
| Accident during initial 30 days | Continue processing the claim |

### Edge Case

**Admission on Day 30:** The exact eligibility interpretation for a non-accident claim admitted on Day 30 will be verified using the project sample data/README or clarified with the project support team before implementation.

### Example

Policy inception date: 1 January 2026  
Admission date: 20 January 2026  
Diagnosis: Normal illness  

Result: **REJECTED** because the 30-day initial waiting period has not been completed.
## BR-02 – Room Rent Limit and Proportionate Deduction

### Purpose
To determine the eligible room rent based on the policy plan and apply proportionate deductions to associated medical charges when the selected room exceeds the allowed limit.

### Rules

1. SILVER plans allow room rent up to 1% of the Sum Insured (SI) per day.
2. GOLD plans allow room rent up to 2% of the Sum Insured (SI) per day.
3. PLATINUM plans have no room rent limit.
4. The ICU room rent limit is twice the applicable room rent limit.
5. If the actual room rent exceeds the eligible room rent limit, associated charges must be proportionately reduced.
6. Associated charges include room charges, nursing charges, doctor visits and surgery charges.
7. The proportionate deduction must be applied before disease/procedure sub-limits.

### Calculation

**Room Rent Limit**

- SILVER = 1% × Sum Insured per day
- GOLD = 2% × Sum Insured per day
- PLATINUM = No limit

**ICU Limit**

ICU Limit = 2 × Room Rent Limit

**Proportionate Factor**

Proportionate Factor = Eligible Room Rent ÷ Actual Room Rent

If the actual room rent is within the allowed limit, the proportionate factor is 1 and no deduction is applied.

### Example

Policy Plan: SILVER  
Sum Insured: ₹5,00,000  
Eligible Room Rent: ₹5,000 per day  
Actual Room Rent: ₹8,000 per day  

Proportionate Factor = ₹5,000 ÷ ₹8,000 = **0.625 (62.5%)**

Therefore, the applicable associated charges are reduced to 62.5% before further limits are applied.

### Edge Case

If the room rent is exactly equal to the allowed limit, the proportionate factor is 1.0 and no proportionate deduction is applied.
## BR-03 – Disease and Procedure Sub-limits

### Purpose
To limit the eligible claim amount for specified diseases and procedures according to the policy plan.

### Rules

1. CATARACT claims are limited to ₹40,000 per eye.
2. KNEE_REPLACEMENT claims are limited to ₹1,50,000.
3. HERNIA claims are limited to ₹60,000 for SILVER and GOLD plans.
4. PLATINUM plans have no disease or procedure sub-limits.
5. Disease sub-limits must be applied after the room proportionate deduction.

### Calculation

Eligible Amount After Sub-limit = Minimum(Amount After Room Proportionate Deduction, Applicable Disease Sub-limit)

### Example

Amount after room proportionate deduction: ₹1,80,000  
Applicable disease sub-limit: ₹1,50,000  

Eligible amount after sub-limit: **₹1,50,000**
## BR-04 – Co-pay

### Purpose
To calculate the portion of the eligible claim amount that must be paid by the customer.

### Rules

1. Members aged 61 years or older on the admission date have a 20% co-pay.
2. Treatment at a Zone C hospital when the policy zone is A has an additional 10% co-pay.
3. Applicable co-pays are added together.
4. The total co-pay percentage cannot exceed 30%.

### Calculation

Total Co-pay % = Minimum(Age Co-pay % + Zone Co-pay %, 30%)

Customer Co-pay Amount = Eligible Claim Amount × Total Co-pay %

Insurance Payable = Eligible Claim Amount − Customer Co-pay Amount

### Edge Case

If both conditions apply, the total co-pay reaches exactly 30% and must not exceed this limit.
## BR-05 – Non-payable Expenses

### Purpose
To deduct hospital expenses that are not covered by the insurance policy.

### Rules

1. Expenses listed as non-payable consumables, such as gloves and admission kits, are deducted fully.
2. If the policy has a CONSUMABLE_COVER rider, eligible consumables are not deducted under this rule.
3. For PLATINUM policies, the total non-payable deduction is capped at 10% of the bill.

### Calculation

For standard policies:

Non-payable Deduction = Total Applicable Non-payable Expenses

For PLATINUM:

Non-payable Deduction = Minimum(Total Applicable Non-payable Expenses, 10% of Bill)

### Example

Total bill: ₹2,00,000  
Applicable non-payables: ₹30,000  
PLATINUM cap: ₹20,000  

Non-payable deduction: **₹20,000**
## BR-06 – Pre-authorisation and Enhancement

### Purpose
To calculate the initial pre-authorisation amount and process valid enhancement requests.

### Initial Approval Rules

The initial approved amount is the minimum of:

1. Estimated bill after applying applicable limits.
2. 60% of the remaining Sum Insured.
3. ₹2,00,000.

### Enhancement Rules

1. An enhancement request may be approved up to the available remaining Sum Insured.
2. An enhancement request must be received before the discharge date.
3. An enhancement received after discharge must be rejected.

### Calculation

Initial Approval = Minimum(
Eligible Estimated Bill,
60% of Remaining SI,
₹2,00,000
)

### Edge Case

An enhancement request timestamped after the discharge date must not be approved.
## BR-06 – Pre-authorisation and Enhancement

### Purpose
To calculate the initial pre-authorisation amount and process valid enhancement requests.

### Initial Approval Rules

The initial approved amount is the minimum of:

1. Estimated bill after applying applicable limits.
2. 60% of the remaining Sum Insured.
3. ₹2,00,000.

### Enhancement Rules

1. An enhancement request may be approved up to the available remaining Sum Insured.
2. An enhancement request must be received before the discharge date.
3. An enhancement received after discharge must be rejected.

### Calculation

Initial Approval = Minimum(
Eligible Estimated Bill,
60% of Remaining SI,
₹2,00,000
)

### Edge Case

An enhancement request timestamped after the discharge date must not be approved.
## BR-07 – Final Bill Settlement

### Purpose
To calculate the final insurance payable amount and the customer's share after receiving the final hospital bill.

### Rules

1. The final payable amount is calculated after applying all applicable limits and co-pay.
2. The insurance payable amount cannot exceed the remaining Sum Insured.
3. The customer pays the balance of the final bill that is not payable by insurance.
4. If the final bill is lower than the initial approved amount, the unused approved amount is released.

### Calculation

Final Payable = Minimum(Eligible Amount After Limits and Co-pay, Remaining SI)

Customer Share = Final Bill − Final Payable

### Edge Case

If the final bill is lower than the initial approved amount, the difference must be released back to the available Sum Insured.
## BR-08 – Pre and Post-Hospitalisation Expenses

### Purpose
To include eligible medical expenses incurred before and after hospitalisation.

### Rules

1. Pre-hospitalisation expenses are eligible only within 30 days before admission.
2. Post-hospitalisation expenses are eligible only within 60 days after discharge.
3. The combined eligible pre- and post-hospitalisation expenses cannot exceed 10% of the admissible hospitalisation claim.
4. These expenses are processed during FINAL_BILL settlement.

### Calculation

Maximum Allowed Expenses = 10% × Admissible Hospitalisation Claim

Eligible Additional Expenses = Minimum(
Eligible Pre/Post-Hospitalisation Expenses,
Maximum Allowed Expenses
)
## BR-09 – Sum Insured Restoration

### Purpose
To restore the policy's Sum Insured after it has been exhausted, subject to specific eligibility conditions.

### Rules

1. Restoration is considered only when the Sum Insured is exhausted after a settled claim.
2. 100% of the Sum Insured may be restored once per policy year.
3. The restored Sum Insured can be used only for an unrelated illness belonging to a different ICD chapter.
4. Restored Sum Insured cannot be used for the same member's same illness.
5. The system must track whether restoration has already been used during the policy year.

### Example

A policy's ₹5,00,000 Sum Insured is fully exhausted after a settled claim for an illness in one ICD chapter.

A later eligible claim for an unrelated illness in a different ICD chapter may use the restored Sum Insured.

A later claim by the same member for the same illness cannot use the restored amount.

### Edge Case

A second claim in the same policy year for the same ICD chapter after restoration must not be allowed to consume restored Sum Insured.
## BR-10 – No-Claim Bonus

### Purpose
To increase available coverage for claim-free years and manage the consumption and reduction of the bonus.

### Rules

1. A claim-free policy year earns a 10% increase in Sum Insured.
2. The maximum accumulated No-Claim Bonus is 50% of the base Sum Insured.
3. Available No-Claim Bonus is consumed before the base Sum Insured.
4. A claim reduces the No-Claim Bonus by 10 percentage points at renewal.

### Example

Base Sum Insured: ₹5,00,000  
No-Claim Bonus: 10% = ₹50,000  

Available coverage: ₹5,50,000.

The ₹50,000 bonus is consumed before the base Sum Insured.
## BR-11 – Query Timeline

### Purpose
To manage claims that require additional information from the hospital.

### Rules

1. The system may place a pre-authorisation request in QUERY status when additional information is required.
2. The hospital must respond within 48 hours of the query.
3. If the hospital does not respond within the permitted timeline, the pre-authorisation is automatically rejected.
4. A rejected pre-authorisation may be resubmitted once.
5. The system must track the number of resubmissions.

### Edge Case

A response received exactly at the 48-hour deadline will be handled according to the deadline interpretation specified in the project sample data/README or confirmed with the project support team.
## BR-12 – Deduction Precedence

### Purpose
To ensure all insurance claim deductions and limits are applied in the correct sequence.

### Required Order

1. Waiting Period
2. Room Proportionate Deduction
3. Disease/Procedure Sub-limit
4. Non-payables
5. Co-pay
6. Sum Insured Cap

### Rules

1. Waiting-period eligibility must be checked before any financial calculation.
2. Room proportionate deduction must be applied before disease or procedure sub-limits.
3. Disease or procedure sub-limits are applied to the amount remaining after the room deduction.
4. Non-payable expenses are deducted after applicable sub-limits.
5. Co-pay is calculated on the eligible amount after previous deductions.
6. The final insurance payment is capped by the available Sum Insured.

### Viva Note

Applying the rules in a different order may change the final payable amount. Therefore, the system follows the required precedence exactly.
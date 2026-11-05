# Health Insurance Cashless Pre-Authorisation and Settlement Engine

## Project Overview

This project is a rule-based Health Insurance Cashless Pre-Authorisation and Settlement Engine. It processes insurance claims through a command-based workflow and applies business rules to determine eligibility, approvals, enhancements, and final settlements.

The system simulates a simplified cashless health insurance claim process from policy registration to final bill settlement.

## Features

- Policy registration
- Member and claim management
- Rule-based claim eligibility checking
- Initial waiting period validation
- Room rent limit calculation
- Disease sub-limit calculation
- Non-payable expense handling
- Co-payment calculation
- Sum insured validation
- Pre-authorisation approval
- Enhancement approval
- Final bill settlement
- Command-based input processing
- Clean text-based output generation
- Automated unit testing

## Project Workflow

```text
REGISTER_POLICY
       ↓
PRE_AUTH
       ↓
ENHANCEMENT
       ↓
FINAL_BILL
       ↓
SETTLED
```

## Project Structure

```text
capstone/
│
├── data/
│   ├── input/
│   │   └── commands.txt
│   │
│   └── output/
│       └── results.txt
│
├── docs/
│   ├── business_rules.md
│   ├── glossary.md
│   ├── claim_state_diagram.md
│   └── class_diagram.md
│
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── rules.py
│   ├── engine.py
│   ├── preauth.py
│   ├── enhancement.py
│   ├── settlement.py
│   ├── store.py
│   ├── command_processor.py
│   ├── command_parser.py
│   ├── command_handler.py
│   └── main.py
│
├── test/
│   └── test_rules.py
│
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11 or later
- pytest

Install the required package:

```bash
pip install pytest
```

## How to Run the Project

Open a terminal inside the project folder and run:

```bash
python -m src.main
```

The program reads commands from:

```text
data/input/commands.txt
```

The results are saved to:

```text
data/output/results.txt
```

## Example Commands

The `commands.txt` file can contain commands such as:

```text
REGISTER_POLICY P001 SILVER 500000
PRE_AUTH P001 M001 HERNIA 150000
ENHANCEMENT C001 50000
FINAL_BILL C001 140000
```

## Example Workflow

### 1. Register Policy

```text
REGISTER_POLICY P001 SILVER 500000
```

Creates a health insurance policy with a sum insured of ₹500,000.

### 2. Pre-Authorisation

```text
PRE_AUTH P001 M001 HERNIA 150000
```

Creates a claim and checks it against the configured business rules.

### 3. Enhancement

```text
ENHANCEMENT C001 50000
```

Requests an additional amount for an existing claim.

### 4. Final Bill Settlement

```text
FINAL_BILL C001 140000
```

Processes the final bill and calculates the settlement result.

## Testing

Run the automated tests using:

```bash
python -m pytest
```

## Business Rules

The engine applies several business rules during claim processing, including:

- Initial waiting period
- Room rent limits
- Disease-specific sub-limits
- Non-payable expenses
- Co-payment
- Sum insured limits
- Pre-authorisation approval limits
- Final settlement rules

Detailed business rules are available in:

```text
docs/business_rules.md
```

## Output

After processing the commands, the system generates a readable result file containing the status and details of each stage of the claim workflow.

Example:

```text
RESULT 1: REGISTER_POLICY
Status: SUCCESS

RESULT 2: PRE_AUTH
Status: SUCCESS
Approved Amount: ₹60000

RESULT 3: ENHANCEMENT
Status: APPROVED
Approved Amount: ₹50000

RESULT 4: FINAL_BILL
Status: SETTLED
```

## Future Improvements

- Persistent database storage
- Support for multiple policies and members
- More detailed hospital and diagnosis data
- Improved settlement reconciliation
- REST API or web interface
- Enhanced reporting and audit logs

## Author

Sheetal K M

B.E. Computer Science & Engineering (Data Science)  
Atria Institute of Technology
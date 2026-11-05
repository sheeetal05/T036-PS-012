# Health Insurance Cashless Pre-Authorisation and Settlement Engine

## Project Overview

This project is a Python-based rules engine that simulates the health insurance cashless claim process.

The system processes a claim through the following stages:

1. Claim eligibility and business rule evaluation
2. PRE_AUTH initial approval
3. ENHANCEMENT request processing
4. FINAL_BILL settlement

The project is designed to apply business rules consistently and calculate the insurance payable amount and customer share.

## Features Implemented

- Policy, Member and Claim models
- Business rule evaluation
- Claim decision engine
- Room rent limit calculation
- Sub-limit calculation
- Non-payable deduction handling
- Co-payment calculation
- Sum Insured limit handling
- PRE_AUTH approval calculation
- ENHANCEMENT request validation
- FINAL_BILL settlement calculation
- Command file reading and parsing
- Basic command handling
- Automated tests using pytest

## Project Structure

```text
capstone/
│
├── data/
│   ├── input/
│   │   └── commands.txt
│   │
│   └── output/
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
│   ├── command_processor.py
│   ├── command_parser.py
│   ├── command_handler.py
│   └── main.py
│
├── test/
│   ├── test_rules.py
│   └── test_workflow.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Workflow

```text
CLAIM
  ↓
BUSINESS RULE EVALUATION
  ↓
CLAIM DECISION
  ↓
PRE_AUTH
  ↓
ENHANCEMENT
  ↓
FINAL_BILL
  ↓
SETTLEMENT
```

## How to Run the Project

Open a terminal in the main project folder and run:

```bash
python -m src.main
```

The program currently uses temporary test data to demonstrate the complete claim workflow.

## How to Run Tests

Install pytest if required:

```bash
python -m pip install pytest
```

Run the tests using:

```bash
python -m pytest
```

## Current Status

The core claim processing workflow has been implemented and tested.

The project currently uses temporary test data while waiting for the official sample data and input files. The command processing structure is ready to be connected to the official data format in the next phase.

## Technologies Used

- Python 3
- pytest
- Git and GitHub

## Future Improvements

- Connect official sample data
- Implement persistent data storage
- Process commands as actual business operations
- Generate structured output files
- Add additional edge-case tests

---

**Capstone Project – Health Insurance Cashless Pre-Authorisation and Settlement Engine**
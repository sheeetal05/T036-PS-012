from src.command_handler import handle_command, handle_all_commands
from src.store import DataStore


def test_register_policy_success():
    """Test successful policy registration."""

    store = DataStore()

    command = {
        "command_type": "REGISTER_POLICY",
        "values": ["P001", "SILVER", "500000"]
    }

    result = handle_command(command, store)

    assert result["status"] == "SUCCESS"
    assert result["policy_id"] == "P001"
    assert store.get_policy("P001") is not None


def test_register_policy_invalid_sum_insured():
    """Test policy registration with invalid sum insured."""

    store = DataStore()

    command = {
        "command_type": "REGISTER_POLICY",
        "values": ["P001", "SILVER", "-500000"]
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Sum insured must be greater than zero."


def test_register_policy_invalid_command():
    """Test REGISTER_POLICY with missing values."""

    store = DataStore()

    command = {
        "command_type": "REGISTER_POLICY",
        "values": ["P001", "SILVER"]
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Invalid REGISTER_POLICY command."


def test_preauth_policy_not_found():
    """Test PRE_AUTH when the policy does not exist."""

    store = DataStore()

    command = {
        "command_type": "PRE_AUTH",
        "values": ["P999", "M001", "HERNIA", "150000"]
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Policy P999 not found."


def test_enhancement_claim_not_found():
    """Test ENHANCEMENT for a claim that does not exist."""

    store = DataStore()

    command = {
        "command_type": "ENHANCEMENT",
        "values": ["C999", "50000"]
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Claim C999 not found."


def test_final_bill_claim_not_found():
    """Test FINAL_BILL for a claim that does not exist."""

    store = DataStore()

    command = {
        "command_type": "FINAL_BILL",
        "values": ["C999", "140000"]
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Claim C999 not found."


def test_unknown_command():
    """Test an unknown command."""

    store = DataStore()

    command = {
        "command_type": "UNKNOWN_COMMAND",
        "values": []
    }

    result = handle_command(command, store)

    assert result["status"] == "ERROR"
    assert result["message"] == "Unknown command: UNKNOWN_COMMAND"


def test_complete_command_workflow():
    """
    Test the complete workflow:
    REGISTER_POLICY -> PRE_AUTH -> ENHANCEMENT -> FINAL_BILL
    """

    store = DataStore()

    commands = [
        {
            "command_type": "REGISTER_POLICY",
            "values": ["P001", "SILVER", "500000"]
        },
        {
            "command_type": "PRE_AUTH",
            "values": ["P001", "M001", "HERNIA", "150000"]
        },
        {
            "command_type": "ENHANCEMENT",
            "values": ["C001", "50000"]
        },
        {
            "command_type": "FINAL_BILL",
            "values": ["C001", "140000"]
        }
    ]

    results = handle_all_commands(commands, store)

    assert len(results) == 4
    assert results[0]["status"] == "SUCCESS"
    assert results[1]["status"] == "SUCCESS"
    assert results[2]["status"] == "APPROVED"
    assert results[3]["status"] == "SETTLED"

    assert store.get_policy("P001") is not None
    assert store.get_claim("C001") is not None
    assert store.get_preauth("C001") is not None
    assert store.get_enhancement("C001") is not None
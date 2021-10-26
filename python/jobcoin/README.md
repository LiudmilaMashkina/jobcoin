Tested with python 3.9

## Running CLI:

1. `cd REPO_ROOT/python`
1. Install requirements: `pip install -r requirements.txt`
1. Run CLI: `python cli.py`
1. Use `add-user <ADDRS>` to register a user. E.g. `add-user 123 345`
1. Transfer some money to the returned deposit address.
1. Check in Web UI that the money have been transferred to the house address.   
1. Withdraw money by running `withdraw <DEPOSIT_ADDR> <WITHDRAWAL_ADDR> <AMOUNT>`. Note that the withdrawal amount + free must be covered by the current balance. It's currently `assert` so it will fail otherwise.    
1. Check the balance in the UI.   

## Running tests
1. `cd REPO_ROOT/python`
1. Run `pytest`

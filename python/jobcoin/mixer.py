from .user_database import UserAccount, Address, InMemoryUserDatabase
from .blockchain_client import BlockchainClient
from .transaction_history import TransactionHistory
from .deposit_processor import DepositProcessor
from decimal import Decimal
import uuid


class Mixer:
    """Mixer concept is described at
    https://docs.google.com/document/d/1mlK67tEY7SvmtUDacVveJXufTWExwlQB3BPGTLyPkG0/edit.
    """
    # TODO: doc init params
    def __init__(self,
                 user_db: InMemoryUserDatabase,
                 transaction_history: TransactionHistory,
                 house_address: Address,
                 dep_processor: DepositProcessor,
                 blockchain: BlockchainClient):
        self._user_db = user_db
        self._transaction_history = transaction_history
        self._house_address = house_address
        self._dep_processor = dep_processor
        self._blockchain = blockchain

    def new_deposit_address(self) -> Address:
        """Generates a new address owned by the Mixer"""
        # TODO: generate a key pair and store it in some secure place. Returns a
        # public key mock for now.
        return uuid.uuid4().hex

    async def add_user(self, user: UserAccount):
        """Registers user account within the mixer."""
        # TODO: check provided addresses was never used before
        await self._user_db.add_user(user)
        self._dep_processor.add_deposit(user.deposit_addr)

    async def withdraw(self, dep_address: Address, target_address: Address, amount: Decimal):
        """Withdraws the money from the Mixer to the user account.
        NOTE: THe mixer is not responsible for handling operation authorization and assumes
        it's a responsibility of the upstream logic (e.g. a web server).
        """
        user = await self._user_db.get_user(dep_address)
        # TODO: handle properly and throw a proper exception
        assert target_address in user.withdrawal_addrs
        cur_balance = await self._transaction_history.compute_balance(user)
        # TODO: handle properly and throw a proper exception
        assert amount * (Decimal(1) + self._transaction_history.fee_percent) <= cur_balance
        await self._blockchain.transfer(self._house_address, target_address, amount)

    async def run_forever(self):
        """Enters the mixer main loop. TODO: doc details"""
        await self._dep_processor.run_forever()



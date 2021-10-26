import asyncio
from . import config
from .user_database import Address
from .blockchain_client import BlockchainClient
from typing import Set


class DepositProcessor:
    """ The processor is responsible for polling the network for new deposits.
    Once it notices and incoming deposit transaction, it transfers the deposited
    coins to the house account.
    """
    # TODO: doc init params
    def __init__(self,
                 blockchain: BlockchainClient,
                 house_address: Address,
                 deposits: Set[Address] = None,
                 delay_seconds: int = config.DEPOSIT_PROCESSOR_DELAY_SECONDS):
        self._deposits = deposits or set()
        self._blockchain = blockchain
        self._house_address = house_address
        self._delay_seconds = delay_seconds

    def add_deposit(self, deposit_address: Address):
        """Adds `deposit_address` do the list of deposits being polled."""
        self._deposits.add(deposit_address)

    async def run_forever(self):
        """Enters the main loop for polling."""
        while True:
            for dep in self._deposits:
                coins = await self._blockchain.get_balance(dep)
                if coins > 0:
                    await self._blockchain.transfer(dep, self._house_address, coins)
            await asyncio.sleep(self._delay_seconds)

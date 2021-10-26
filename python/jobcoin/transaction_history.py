from .user_database import UserAccount, Address
from .blockchain_client import BlockchainClient
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TransactionHistory:
    """TransactionHistory is responsible for computing balance from the transaction history.
    The balance is computed by analyzing user related transactions and deducing Mixer fee.
    """

    blockchain: BlockchainClient
    fee_percent: Decimal  # TODO: can be changed to table with fees history to support change of fees over time
    house_addr: Address

    async def compute_balance(self, user_acc: UserAccount) -> Decimal:
        """Computes the balance of the `user_acc`."""
        # TODO: this method is expensive, depending on the load some cache can be added later.
        deposit_transactions = await self.blockchain.get_transactions(user_acc.deposit_addr)
        withdrawal_transactions = []
        for addr in user_acc.withdrawal_addrs:
            withdrawal_transactions.extend(await self.blockchain.get_transactions(addr))

        inbound = sum(
            (t.amount for t in deposit_transactions if t.dst == user_acc.deposit_addr),
            start=Decimal(0)
        )
        outbound = sum(
            (t.amount for t in withdrawal_transactions if t.src == self.house_addr),
            start=Decimal(0)
        )
        fees = self.fee_percent * outbound
        return inbound - outbound - fees

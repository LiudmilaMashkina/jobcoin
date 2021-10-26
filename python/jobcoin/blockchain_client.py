from datetime import datetime
from . import config
from .user_database import Address
from dataclasses import dataclass
from typing import List
from decimal import Decimal
import aiohttp


# TODO: use marshmallow for parsing
@dataclass(frozen=True)
class Transaction:
    """Transaction model
    :timestamp: timezone-aware timestamp
    """
    src: Address
    dst: Address
    amount: Decimal
    timestamp: datetime


# TODO: add models for request/response bodies
# TODO: handle errors
class BlockchainClient:
    """Blockchain client is a gateway to the blockchain API. All API
    calls must go through it. It's a single point for adding tracing,
    retries, authorisation etc.
    """

    async def transfer(self, src: Address, dst: Address, amount: Decimal):
        """Transfer the specified `amount` from `src` to `dst`."""
        async with aiohttp.ClientSession() as session:
            async with session.post(config.API_TRANSACTIONS_URL, json={
                'fromAddress': src,
                'toAddress': dst,
                'amount': str(amount)
            }) as response:
                # TODO: handle error
                assert response.status == 200

    async def get_transactions(self, address: Address) -> List[Transaction]:
        """Returns a list of all transactions in which `address` is participating.
        Note: does not return coin creation transaction (e.g. from Web UI).
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{config.API_ADDRESS_URL}/{address}') as response:
                # TODO: handle error
                assert response.status == 200
                body = await response.json()

                def dt(s: str) -> datetime:
                    return datetime.fromisoformat(s.replace('Z', '+00:00'))

                return [
                    Transaction(t['fromAddress'],
                                t['toAddress'],
                                Decimal(t['amount']),
                                dt(t['timestamp']))
                    for t in body['transactions']
                ]

    async def get_balance(self, address: Address) -> Decimal:
        """Returns the amount of coins owned by the `address`."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{config.API_ADDRESS_URL}/{address}') as response:
                # TODO: handle error
                assert response.status == 200
                body = await response.json()

                return Decimal(body['balance'])


#!/usr/bin/env python
import asyncio
import pytest

from ..jobcoin.mixer import TransactionHistory, Mixer, DepositProcessor, BlockchainClient
from ..jobcoin.user_database import InMemoryUserDatabase, UserAccount, Address
from ..jobcoin.config import DEPOSIT_PROCESSOR_DELAY_SECONDS
import uuid
from decimal import Decimal


# TODO: test wallet must have money on it. It will run out after ~500 test runs
# to fix add API to test blockchain to allow minting coins.
TEST_WALLET = 'TestWallet'
TEST_BALANCE = Decimal('0.01')
TEST_FEE = Decimal('0.02')


def gen_address() -> Address:
    return uuid.uuid4().hex


@pytest.mark.asyncio
async def test_basic():
    # TODO: create some helpers for initializing and shutting down common stuff
    # TODO: add service authorisation
    service_client = BlockchainClient()
    user_db = InMemoryUserDatabase()
    house_address = gen_address()
    transaction_history = TransactionHistory(service_client, TEST_FEE, house_address)
    dep_processor = DepositProcessor(service_client, house_address)
    mixer = Mixer(user_db, transaction_history, house_address, dep_processor, service_client)
    mixer_task = asyncio.create_task(mixer.run_forever())

    dep_addr = mixer.new_deposit_address()
    target_address = gen_address()
    user = UserAccount(dep_addr, {target_address})
    # TODO: add user authorization
    user_client = BlockchainClient()

    # test add new user and transfer money
    await mixer.add_user(user)
    await user_client.transfer(TEST_WALLET, dep_addr, TEST_BALANCE)
    await asyncio.sleep(DEPOSIT_PROCESSOR_DELAY_SECONDS * 5)
    house_balance_after_deposit = await service_client.get_balance(house_address)
    assert house_balance_after_deposit == TEST_BALANCE

    # test withdraw
    await mixer.withdraw(dep_addr, target_address, TEST_BALANCE / 2)
    house_balance_after_withdrawal = await service_client.get_balance(house_address)
    assert house_balance_after_deposit - house_balance_after_withdrawal == TEST_BALANCE / 2
    user_withdrawal_balance = await user_client.get_balance(target_address)
    assert user_withdrawal_balance == TEST_BALANCE / 2
    left_user_balance = await transaction_history.compute_balance(user)
    assert left_user_balance == TEST_BALANCE / 2 * (1 - TEST_FEE)

    # TODO: make sure the task is cancelled even if the test fails
    mixer_task.cancel()
    try:
        await mixer_task
    except asyncio.CancelledError:
        pass


# TODO: other cases to test
# 1. Test addresses provided were never used before.
# 2. Test not enough money on the Mixer balance.
# 3. Test access by wrong or not owned deposit address. (not a Mixer but upstream logic test)
# 4. Validate withdraw address belongs to the UserAccount registered with the Mixer.
# 5. Test error handling in the BlockchainClinet. I.e. when the client throws an Exception the Mixer should fail gracefully.


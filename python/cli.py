#!/usr/bin/env python
import uuid
from decimal import Decimal
from jobcoin.mixer import TransactionHistory, Mixer, DepositProcessor, BlockchainClient
from jobcoin.user_database import InMemoryUserDatabase, UserAccount
import asyncio
from click import UsageError, Abort
from typing import List
import typer
import sys
import inspect


async def read_command(reader: asyncio.StreamReader):
    """Asynchronously reads the next command."""

    print('Enter command: ', end='', flush=True)
    chars: List[str] = []
    while True:
        c = (await reader.read(1)).decode('utf-8')
        if c == '\n':
            return ''.join(chars)
        else:
            chars.append(c)


async def run_cli(mixer: Mixer):
    app = typer.Typer()

    @app.command()
    # expected format: add-user addr1 addr2 addr3
    async def add_user(addresses: List[str] = typer.Argument(..., help="unused addresses")):
        """Provide several unused addresses. Example: address1 address2 address3"""
        deposit_address = mixer.new_deposit_address()
        print(f'Your new deposit address: {deposit_address}')
        user = UserAccount(deposit_address, set(addresses))
        await mixer.add_user(user)

    @app.command()
    # expected format: withdraw deposit_addr withdraw_addr 13.75
    async def withdraw(deposit: str, target_address: str, amount: str):
        # TODO: make better 'help' info
        """Provide your deposit address, target address and amount to withdraw, separated by spaces."""
        print(f'widhdraw: from deposit = {deposit}, to = {target_address} {amount} Jobcoins')
        await mixer.withdraw(deposit, target_address, Decimal(amount))

    print('Welcome to the Jobcoin mixer!')
    print('Type `help` for help. Ctrl+C to exit.')

    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            s = await read_command(reader)
            if s == 'help':
                app(['--help'], standalone_mode=False)
            else:
                maybe_coro = app(s.split(), standalone_mode=False)
                if inspect.iscoroutine(maybe_coro):
                    await maybe_coro
        except UsageError as e:
            print(e)
        except Abort:
            return


async def main():
    blockchain_client = BlockchainClient()
    user_db = InMemoryUserDatabase()
    house_address = f'house_{uuid.uuid4().hex}'
    transaction_history = TransactionHistory(blockchain_client, Decimal(1), house_address)
    dep_processor = DepositProcessor(blockchain_client, house_address)
    mixer = Mixer(user_db, transaction_history, house_address, dep_processor, blockchain_client)
    mixer_task = asyncio.create_task(mixer.run_forever())
    # TODO: cancel mixer_task at the end.

    await run_cli(mixer)


if __name__ == '__main__':
    asyncio.run(main())

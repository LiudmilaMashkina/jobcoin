from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Set


Address = str


@dataclass(frozen=True)
class UserAccount:
    """UserAccount model."""
    deposit_addr: Address
    withdrawal_addrs: Set[Address]


# TODO: add some real database to store user account data
class UserDatabase(ABC):
    """User storage interface."""
    @abstractmethod
    async def get_user(self, deposit_addr: Address):
        """Returns the user associated with the `deposit_addr`"""
        pass

    @abstractmethod
    async def add_user(self, user: UserAccount):
        """Stores given `user`."""
        pass


class InMemoryUserDatabase(UserDatabase):
    """In-memory [UserDatabase] implementation.
    """
    def __init__(self):
        self._users: Dict[Address, UserAccount] = {}

    async def get_user(self, deposit_addr: Address):
        # TODO: handle nonexistent deposit address
        return self._users[deposit_addr]

    async def add_user(self, user: UserAccount):
        # TODO: check the user doesn't exist
        self._users[user.deposit_addr] = user

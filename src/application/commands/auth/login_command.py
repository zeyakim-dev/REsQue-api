from dataclasses import dataclass
from typing import Protocol

from src.domain.user.user import User


class UserRepository(Protocol):
    def save(self, user: User) -> None:
        pass


@dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str

    def execute(self, user_repository, password_hasher):
        pass

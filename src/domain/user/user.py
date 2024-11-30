from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class IdGenerator(Protocol):
    def generate(self) -> UUID: ...


@dataclass(frozen=True)
class User:
    username: str
    hashed_password: str
    id: UUID

    @staticmethod
    def create(
        user_info: dict, password_hasher: PasswordHasher, id_generator: IdGenerator
    ) -> "User":
        return User(
            id=id_generator.generate(),
            username=user_info["username"],
            hashed_password=password_hasher.hash(user_info["password"]),
        )

    def verify_password(self, password: str, password_hasher: PasswordHasher) -> bool:
        hashed_password = password_hasher.hash(password)
        return self.hashed_password == hashed_password

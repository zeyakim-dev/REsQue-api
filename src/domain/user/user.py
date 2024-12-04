from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from src.domain.entity import Entity


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hashed_password: str) -> bool: ...

class IdGenerator(Protocol):
    def generate(self) -> UUID: ...

@dataclass(frozen=True)
class User(Entity):
    username: str
    hashed_password: str

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
        """비밀번호를 검증합니다.
        
        Args:
            password: 검증할 평문 비밀번호
            password_hasher: 비밀번호 해시 유틸리티
            
        Returns:
            bool: 비밀번호가 일치하면 True
        """
        return password_hasher.verify(password, self.hashed_password)
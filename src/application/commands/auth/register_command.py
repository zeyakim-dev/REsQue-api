
from dataclasses import dataclass
from typing import Protocol

from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator
from src.domain.user.user import User

class UserRepository(Protocol):
    def save(self, user: User) -> None:
        pass

@dataclass(frozen=True)
class RegisterCommand:
    username: str
    password: str
    
    def execute(self, user_repository: UserRepository, id_generator: UUIDv7Generator, password_hasher: PasswordHasher) -> None:
        new_user = User.create(
            user_info=self.__dict__,
            password_hasher=password_hasher,
            id_generator=id_generator
        )
        
        user_repository.save(new_user)
        
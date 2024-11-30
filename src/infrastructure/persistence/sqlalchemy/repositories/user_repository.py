from typing import Optional
from uuid import UUID
from src.application.ports.repositories.user.user_repository import UserRepository
from src.domain.user.user import User


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        self._session = session
        
    def save(self, user: User) -> None:
        # 구현
        pass
        
    def find_by_id(self, id: UUID) -> Optional[User]:
        # 구현
        pass
        
    def find_by_username(self, username: str) -> Optional[User]:
        # 구현
        pass
        
    def exists_by_username(self, username: str) -> bool:
        # 구현
        pass
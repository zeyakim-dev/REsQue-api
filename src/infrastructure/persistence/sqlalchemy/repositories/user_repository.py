from typing import Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.application.ports.repositories.user.user_repository import UserRepository
from src.domain.user.user import User
from src.infrastructure.persistence.sqlalchemy.models.users import UserModel
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository

class SQLAlchemyUserRepository(SQLAlchemyRepository[UserModel, User], UserRepository):
    """SQLAlchemy를 사용하는 사용자 저장소 구현체"""
    
    def __init__(self, session):
        """저장소를 초기화합니다.

        Args:
            session: SQLAlchemy 세션
        """
        super().__init__(session, UserModel)

    def _to_model(self, entity: User) -> UserModel:
        """도메인 엔티티를 ORM 모델로 변환합니다.

        Args:
            entity: 변환할 User 엔티티

        Returns:
            UserModel: 변환된 ORM 모델
        """
        return UserModel(
            id=entity.id,
            username=entity.username,
            hashed_password=entity.hashed_password
        )
    
    def _to_domain(self, model: UserModel) -> User:
        """ORM 모델을 도메인 엔티티로 변환합니다.

        Args:
            model: 변환할 UserModel

        Returns:
            User: 변환된 도메인 엔티티
        """
        return User(
            id=model.id,
            username=model.username,
            hashed_password=model.hashed_password
        )

    def find_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자를 조회합니다.
    
        Args:
            username: 조회할 사용자명
            
        Returns:
            Optional[User]: 찾은 사용자 엔티티, 없으면 None
        """
        result = self._session.query(self._model_type).filter_by(username=username).first()
        return self._to_domain(result) if result else None

    def exists_by_username(self, username: str) -> bool:
        """사용자명이 존재하는지 확인합니다.

        Args:
            username: 확인할 사용자명

        Returns:
            bool: 사용자명 존재 여부
        """
        stmt = select(1).where(UserModel.username == username)
        result = self._session.scalar(stmt)
        return bool(result)

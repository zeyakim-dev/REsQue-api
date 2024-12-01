from sqlalchemy.orm import Session
from typing import Optional

from src.application.ports.uow import UnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy를 사용하는 UnitOfWork 구현체입니다."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session: Optional[Session] = None
        self._repository: Optional[SQLAlchemyUserRepository] = None

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        """트랜잭션을 시작하고 새로운 세션과 레포지토리를 생성합니다."""
        if self._session is not None:
            raise RuntimeError("이미 활성화된 UnitOfWork가 존재합니다")
            
        self._session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """트랜잭션을 종료하고 세션을 정리합니다.
        
        예외가 발생했다면 롤백하고, 그렇지 않으면 변경사항을 유지합니다.
        마지막으로 세션을 종료합니다.
        """
        try:
            if exc_type:
                self.rollback()
        finally:
            if self._session:
                self._session.close()
                self._session = None
                self._repository = None

    def commit(self) -> None:
        """현재 트랜잭션의 모든 변경사항을 데이터베이스에 반영합니다."""
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
            
        try:
            self._session.commit()
        except:
            self.rollback()
            raise

    def rollback(self) -> None:
        """현재 트랜잭션의 모든 변경사항을 취소합니다."""
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
            
        self._session.rollback()

    @property
    def repository(self) -> SQLAlchemyUserRepository:
        """현재 세션에 바인딩된 레포지토리를 반환합니다."""
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
            
        if self._repository is None:
            self._repository = SQLAlchemyUserRepository(self._session)
            
        return self._repository
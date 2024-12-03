from typing import Protocol, Type, TypeVar, Dict, Callable
from sqlalchemy.orm import Session
from typing import Optional
from src.application.ports.uow import UnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository

T = TypeVar("T", bound=SQLAlchemyRepository)

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy를 사용하는 UnitOfWork 구현체입니다."""
    
    def __init__(self, session_factory, repositories: Dict[Type[T], Callable[[Session], T]]):
        """
        Args:
            session_factory: SQLAlchemy 세션 팩토리
            repositories: 레포지토리 타입을 키로, 레포지토리 생성 팩토리를 값으로 가지는 딕셔너리
        """
        self.session_factory = session_factory
        self.repository_factories = repositories
        self._session: Optional[Session] = None
        self._repositories: Dict[Type[T], T] = {}

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        """트랜잭션을 시작하고 새로운 세션을 생성합니다."""
        if self._session is not None:
            raise RuntimeError("이미 활성화된 UnitOfWork가 존재합니다")
            
        self._session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """트랜잭션을 종료하고 세션을 정리합니다."""
        try:
            if exc_type:
                self.rollback()
        finally:
            if self._session:
                self._session.close()
                self._session = None
                self._repositories.clear()

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

    def get_repository(self, repository_type: Type[T]) -> T:
        """요청된 타입의 레포지토리를 반환합니다.
        
        Args:
            repository_type: 원하는 레포지토리의 타입
            
        Returns:
            해당 타입의 레포지토리 인스턴스
            
        Raises:
            RuntimeError: UnitOfWork가 활성화되지 않은 경우
            KeyError: 지원하지 않는 레포지토리 타입인 경우
        """
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")

        if repository_type not in self._repositories:
            if repository_type not in self.repository_factories:
                raise KeyError(f"지원하지 않는 레포지토리 타입입니다: {repository_type}")
                
            factory = self.repository_factories[repository_type]
            self._repositories[repository_type] = factory(self._session)

        return self._repositories[repository_type]
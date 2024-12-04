from typing import Protocol, Type, TypeVar, Dict, Callable
from sqlalchemy.orm import Session
from typing import Optional
from src.application.ports.uow import UnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository

T = TypeVar("T", bound=SQLAlchemyRepository)

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory, repositories: Dict[Type[T], Callable[[Session], T]]):
        super().__init__()  # 부모 클래스 초기화 호출
        self.session_factory = session_factory
        self.repository_factories = repositories
        self._session: Optional[Session] = None
        self._repositories: Dict[Type[T], T] = {}

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        if self._session is not None:
            raise RuntimeError("이미 활성화된 UnitOfWork가 존재합니다")
        self._session = self.session_factory()
        return self

    def __exit__(self, *args) -> None:
        if self._session:
            self._session.close()
            self._session = None
            self._repositories.clear()

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
        self._session.rollback()

    def get_repository(self, repository_type: Type[T]) -> T:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")

        if repository_type not in self._repositories:
            if repository_type not in self.repository_factories:
                raise KeyError(f"지원하지 않는 레포지토리 타입입니다: {repository_type}")
            
            factory = self.repository_factories[repository_type]
            self._repositories[repository_type] = factory(self._session)

        return self._repositories[repository_type]
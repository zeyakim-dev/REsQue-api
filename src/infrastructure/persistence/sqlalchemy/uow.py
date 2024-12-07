from typing import Callable, Dict, Optional, Protocol, Type, TypeVar

from sqlalchemy.orm import Session

from src.application.ports.repositories.repository import Repository
from src.application.ports.uow import UnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import (
    SQLAlchemyRepository,
)

R = TypeVar("R", bound=Repository)
T = TypeVar("T", bound=SQLAlchemyRepository)


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self, session_factory, repositories: Dict[Type[R], Callable[[Session], T]]
    ):
        super().__init__()
        self.session_factory = session_factory
        self.repository_factories = repositories
        self._session: Optional[Session] = None
        self._repositories: Dict[Type[T], T] = {}

    def _begin(self) -> "SQLAlchemyUnitOfWork":
        """UnitOfWork 작업을 시작합니다."""
        if self._session is not None:
            raise RuntimeError("이미 활성화된 UnitOfWork가 존재합니다")
        self._session = self.session_factory()
        return self

    def __exit__(self, *args) -> None:
        """부모의 __exit__을 호출한 후 세션을 정리합니다."""
        try:
            super().__exit__(*args)
        finally:
            if self._session:
                self._session.close()
                self._session = None
                self._repositories.clear()

    def _commit(self) -> None:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
        self._session.commit()

    def _rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")
        self._session.rollback()

    def get_repository(self, repository_type: Type[T]) -> T:
        if self._session is None:
            raise RuntimeError("활성화된 UnitOfWork가 없습니다")

        # 1. 기존 캐시된 레포지토리가 있는지 확인
        repository = self._repositories.get(repository_type)
        if repository is not None:
            return repository

        # 2. 팩토리 확인
        factory = self.repository_factories.get(repository_type)
        if factory is None:
            raise KeyError(
                f"지원하지 않는 레포지토리 타입입니다: {repository_type.__name__}"
            )

        # 3. 새 레포지토리 생성 및 캐싱
        repository = factory(self._session)  # 팩토리로 새 인스턴스 생성
        self._repositories[repository_type] = repository

        return repository

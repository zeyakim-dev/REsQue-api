from abc import abstractmethod
from typing import Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.ports.repositories.repository import Repository
from src.domain.entity import Entity

Model = TypeVar("Model")
Domain = TypeVar("Domain", bound=Entity)


class SQLAlchemyRepository(Repository[Domain], Generic[Model, Domain]):
    """SQLAlchemy를 사용하는 기본 Repository 구현체"""

    def __init__(self, session: Session, model_type: Type[Model]):
        """
        Args:
            session: SQLAlchemy session
            model_type: SQLAlchemy model class
        """
        super().__init__()
        self._session = session
        self._model_type = model_type

    def _add(self, entity: Domain) -> None:
        """도메인 엔티티를 저장소에 추가합니다."""
        model = self._to_model(entity)
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as e:
            self._session.rollback()  # rollback 추가
            raise e

    def _get(self, id: UUID) -> Optional[Domain]:
        """ID로 도메인 엔티티를 조회합니다.

        Args:
            id: 조회할 엔티티의 ID

        Returns:
            Optional[Domain]: 조회된 도메인 엔티티 또는 None
        """
        model = self._session.query(self._model_type).filter_by(id=id).first()
        if model is not None:
            return self._to_domain(model)
        return None

    @abstractmethod
    def _to_model(self, entity: Domain) -> Model:
        """도메인 엔티티를 ORM 모델로 변환합니다.

        Args:
            entity: 변환할 도메인 엔티티

        Returns:
            변환된 ORM 모델
        """
        raise NotImplementedError

    @abstractmethod
    def _to_domain(self, model: Model) -> Domain:
        """ORM 모델을 도메인 엔티티로 변환합니다.

        Args:
            model: 변환할 ORM 모델

        Returns:
            변환된 도메인 엔티티
        """
        raise NotImplementedError

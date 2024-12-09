from abc import abstractmethod
from typing import Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.ports.repositories.repository import Repository
from src.domain.shared.aggregate_root import AggregateRoot

# SQLAlchemy 모델을 위한 타입 변수
Model = TypeVar("Model")

# 도메인 타입을 AggregateRoot로 제한하는 타입 변수
Domain = TypeVar("Domain", bound=AggregateRoot)


class SQLAlchemyRepository(Repository[Domain], Generic[Model, Domain]):
    """
    SQLAlchemy를 사용하는 기본 Repository 구현체입니다.
    모든 SQLAlchemy 기반 레포지토리의 기본 클래스로 사용됩니다.
    """

    def __init__(self, session: Session, model_type: Type[Model]):
        """
        레포지토리를 초기화합니다.

        Args:
            session: 데이터베이스 작업에 사용할 SQLAlchemy 세션
            model_type: 이 레포지토리가 다룰 SQLAlchemy 모델의 타입
        """
        super().__init__()
        self._session = session
        self._model_type = model_type

    def _add(self, aggregate: Domain) -> None:
        """
        애그리게이트 루트를 저장소에 추가합니다.
        변환 중 발생하는 무결성 위반은 IntegrityError로 처리됩니다.

        Args:
            aggregate: 저장할 애그리게이트 루트 인스턴스
        
        Raises:
            IntegrityError: 데이터베이스 무결성 제약 조건 위반 시
        """
        model = self._to_model(aggregate)
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as e:
            self._session.rollback()
            raise e

    def _get(self, id: UUID) -> Optional[Domain]:
        """
        ID로 애그리게이트 루트를 조회합니다.

        Args:
            id: 조회할 애그리게이트 루트의 ID

        Returns:
            조회된 애그리게이트 루트 또는 None
        """
        model = self._session.query(self._model_type).filter_by(id=id).first()
        if model is not None:
            return self._to_domain(model)
        return None

    @abstractmethod
    def _to_model(self, aggregate: Domain) -> Model:
        """
        애그리게이트 루트를 SQLAlchemy 모델로 변환합니다.
        이 메서드는 각 구체적인 레포지토리 구현체에서 정의되어야 합니다.

        Args:
            aggregate: 변환할 애그리게이트 루트 인스턴스

        Returns:
            변환된 SQLAlchemy 모델 인스턴스
        """
        raise NotImplementedError

    @abstractmethod
    def _to_domain(self, model: Model) -> Domain:
        """
        SQLAlchemy 모델을 애그리게이트 루트로 변환합니다.
        이 메서드는 각 구체적인 레포지토리 구현체에서 정의되어야 합니다.

        Args:
            model: 변환할 SQLAlchemy 모델 인스턴스

        Returns:
            변환된 애그리게이트 루트 인스턴스
        """
        raise NotImplementedError
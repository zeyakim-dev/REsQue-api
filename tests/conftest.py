from datetime import timedelta
from typing import Callable, Dict, Type

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.persistence.sqlalchemy.models.base import Base
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import (
    SQLAlchemyRepository,
)
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


@pytest.fixture(scope="session")
def engine():
    """테스트용 SQLite 엔진을 생성합니다."""
    engine = create_engine("sqlite:///:memory:")
    return engine


@pytest.fixture(scope="session")
def tables(engine):
    """테스트에 필요한 테이블을 생성합니다."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """테스트용 데이터베이스 세션을 제공합니다."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def repository_factories(
    db_session,
) -> Dict[Type[SQLAlchemyRepository], Callable[[Session], SQLAlchemyRepository]]:
    """레포지토리 팩토리들을 제공합니다."""
    return {
        UserRepository: lambda session: SQLAlchemyUserRepository(session)
        # 추가 레포지토리들은 여기에 등록
    }


@pytest.fixture
def uow(db_session, repository_factories):
    """통합 테스트를 위한 UnitOfWork를 제공합니다."""
    from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork

    return SQLAlchemyUnitOfWork(
        session_factory=lambda: db_session, repositories=repository_factories
    )


# 자주 사용되는 공통 의존성들도 conftest에 추가
@pytest.fixture
def password_hasher():
    from src.infrastructure.security.password_hasher import PasswordHasher

    return PasswordHasher()


@pytest.fixture
def token_generator():
    from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator

    return JWTTokenGenerator("test_secret_key", timedelta(hours=1))


@pytest.fixture
def id_generator():
    from src.infrastructure.uuid.uuid_generator import UUIDv7Generator

    return UUIDv7Generator()

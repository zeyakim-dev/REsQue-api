from typing import Callable, Dict, Type

import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker

from src.application.ports.repositories.repository import Repository
from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.persistence.database_factory import DatabaseFactory
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import (
    SQLAlchemyRepository,
)
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork


class SQLAlchemyDatabaseFactory(DatabaseFactory):
    repository_factory: Dict[
        Type[Repository], Callable[[Session], SQLAlchemyRepository]
    ] = {UserRepository: lambda session: SQLAlchemyUserRepository(session=session)}

    def create_engine(self):
        return sqlalchemy.create_engine(
            url=self.config["url"], connect_args=self.config["connect_args"]
        )

    def create_session_factory(self, db_engine):
        return sessionmaker(bind=db_engine)

    def create_uow(self, session_factory):
        return SQLAlchemyUnitOfWork(
            session_factory=session_factory, repositories=self.repository_factory
        )

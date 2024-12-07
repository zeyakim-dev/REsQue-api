from abc import ABC, abstractmethod
from typing import Dict, Type


class DatabaseFactory(ABC):
    def __init__(self, configuration: Dict):
        self.config = configuration

    @abstractmethod
    def create_engine(self):
        raise NotImplementedError

    @abstractmethod
    def create_session_factory(self, db_engine):
        raise NotImplementedError

    @abstractmethod
    def create_uow(self, session_factory):
        raise NotImplementedError

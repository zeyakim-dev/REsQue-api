
from typing import Dict, Type
from src.infrastructure.persistence.database_factory import DatabaseFactory
from src.infrastructure.persistence.sqlalchemy.sqlalchemy_database_factory import SQLAlchemyDatabaseFactory


class DatabaseFactoryFactory:
    database_factory_factory: Dict[str, Type[DatabaseFactory]] = {
        'sqlite': SQLAlchemyDatabaseFactory
    }

    def __init__(self, configuration: Dict):
        self.db_type = configuration['type']
        self.db_config = configuration['config']
        print(f"Initializing with db_type: {self.db_type}")
        
    def create_database_factory(self) -> DatabaseFactory:
        creator = self.database_factory_factory.get(self.db_type)
        
        return creator(configuration=self.db_config)
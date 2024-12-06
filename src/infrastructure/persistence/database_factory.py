from typing import Dict

from src.infrastructure.persistence.sqlalchemy.config import create_sqlite_engine

class DatabaseFactory:
    engine_factory = {
        'sqlite': create_sqlite_engine
    }
    
    @classmethod
    def create_engine(cls, configuration: Dict):
        db_section = configuration['persistence']
        db_type = db_section['type']
        db_config = db_section['config']

        creator = cls.engine_factory.get(db_type)
        if not creator:
            raise ValueError(f"Unsupported database type: {db_type}")

        return creator(db_config)

class SessionFactoryFactory:
    ...
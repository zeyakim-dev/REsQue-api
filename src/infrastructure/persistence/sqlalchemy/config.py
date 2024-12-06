from typing import Dict
from sqlalchemy import create_engine

def create_sqlite_engine(config: Dict):
    return create_engine(
        url=config['url'],
        connect_args=config['connect_args']
    )
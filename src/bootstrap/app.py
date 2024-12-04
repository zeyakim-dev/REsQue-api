

from typing import Dict
from flask import Flask

from src.bootstrap.bootstrap import Bootstrap


def create_app(config: Dict) -> Flask:
    bootstrap = Bootstrap(config)
    return bootstrap.create_app()
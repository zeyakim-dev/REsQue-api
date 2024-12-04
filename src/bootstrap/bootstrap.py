from typing import Dict
from flask import Flask
from dependency_injector.wiring import inject, Provide
from src.infrastructure.container import Container
from src.interfaces.api import api


class Bootstrap:
    """DDD 애플리케이션의 부트스트랩을 담당하는 클래스입니다."""

    def __init__(self, config: Dict):
        self.container = Container()
        self.container.config.from_dict(config)
        self.container.wire(packages=[
            "src.interfaces",
            "src.application",
            "src.infrastructure"
        ])

    def create_app(self) -> Flask:
        """Flask 애플리케이션을 생성하고 초기화합니다."""
        app = Flask(__name__)
        
        # 컨테이너를 Flask 앱에 연결
        app.container = self.container
        
        # 블루프린트 등록
        self._register_blueprints(app)
        
        return app

    def _register_blueprints(self, app: Flask):
        """블루프린트를 등록합니다."""
        app.register_blueprint(api)

from flask import Flask
from src.infrastructure.container import Container
from src.infrastructure.flask.extensions import FlaskContainer
from src.interfaces.api import api

class Bootstrap:
    """애플리케이션의 부트스트래핑을 담당하는 클래스입니다."""

    def __init__(self, config_path: str):
        self.container = Container()
        self.container.config.from_yaml(str(config_path))

        # 의존성 주입 설정
        self.container.wire(packages=[
            "src.interfaces",
            "src.application",
            "src.infrastructure"
        ])
        
        # Flask 확장 초기화
        self.flask_container = FlaskContainer()
        
    def create_app(self) -> Flask:
        app = Flask(__name__)
        
        # 컨테이너 확장 초기화
        self.flask_container.init_app(app, self.container)
        
        # 블루프린트 등록
        self._register_blueprints(app)
        
        return app
        
    def _register_blueprints(self, app: Flask):
        app.register_blueprint(api)
from typing import Optional, TypeVar

from dependency_injector.containers import Container
from flask import Flask, current_app

T = TypeVar("T")


class FlaskContainer:
    def __init__(
        self, app: Optional[Flask] = None, container: Optional[Container] = None
    ):
        self.app = app
        self.container = container

        if app is not None and container is not None:
            self.init_app(app, container)

    def init_app(self, app: Flask, container: Container):
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["di_container"] = container

        # 리소스 정리를 위한 종료 시점 훅 추가
        @app.teardown_appcontext
        def cleanup_container(exception=None):
            if "di_container" in app.extensions:
                # 필요한 리소스 정리 로직
                pass

    def _setup_request_hooks(self, app: Flask):
        """요청 컨텍스트 훅을 설정합니다."""

        @app.before_request
        def before_request():
            """요청 처리 전에 필요한 초기화를 수행합니다."""
            pass  # 필요한 경우 요청별 초기화 로직 추가

        @app.teardown_request
        def teardown_request(exception=None):
            """요청 처리 후 정리 작업을 수행합니다."""
            pass  # 필요한 경우 정리 로직 추가

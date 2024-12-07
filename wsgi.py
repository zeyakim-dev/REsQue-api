import os
from pathlib import Path

from src.bootstrap.app import create_app


def get_config_path(env: str) -> str:
    """환경에 따른 설정 파일 경로를 반환합니다."""
    config_dir = Path(__file__).parent / "src" / "config"
    return str(config_dir / f"{env}.yaml")


# WSGI 애플리케이션 생성
env = os.getenv("FLASK_ENV", "dev")
application = create_app(config_path=get_config_path(env))

# 개발 서버 실행 (python wsgi.py로 직접 실행 시)
if __name__ == "__main__":
    application.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=True,
    )

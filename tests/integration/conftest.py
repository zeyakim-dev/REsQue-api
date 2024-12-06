import time
from typing import Generator
import docker
import pytest
from src.bootstrap.app import create_app
from flask import Flask
from pathlib import Path

from src.infrastructure.persistence.sqlalchemy.models.base import Base


@pytest.fixture(scope="session")
def rabbitmq_container() -> Generator[docker.models.containers.Container, None, None]:
    """RabbitMQ 테스트 컨테이너를 관리합니다."""
    import docker.errors
    client = docker.from_env()
    container = None

    try:
        # 기존 컨테이너 정리
        try:
            old_container = client.containers.get('test-rabbitmq')
            print("기존 컨테이너를 정리합니다...")
            old_container.stop()
            old_container.remove()
            print("기존 컨테이너가 성공적으로 제거되었습니다.")
        except docker.errors.NotFound:
            print("제거할 기존 컨테이너가 없습니다.")

        print("새로운 RabbitMQ 컨테이너를 시작합니다...")
        container = client.containers.run(
            'rabbitmq:3-management',
            name='test-rabbitmq',
            ports={
                '5672/tcp': 5672,
                '15672/tcp': 15672
            },
            environment={
                'RABBITMQ_DEFAULT_USER': 'guest',
                'RABBITMQ_DEFAULT_PASS': 'guest'
            },
            detach=True,
            remove=True
        )

        # 컨테이너 시작 확인
        start_time = time.time()
        timeout = 60  # 60초 타임아웃
        while time.time() - start_time < timeout:
            try:
                # 컨테이너 상태 새로 가져오기
                container.reload()
                
                # 로그 확인
                logs = container.logs().decode('utf-8')
                if "Server startup complete" in logs:
                    print("RabbitMQ 서버가 성공적으로 시작되었습니다!")
                    break
                    
            except docker.errors.NotFound:
                print("컨테이너를 찾을 수 없습니다. 재시도합니다...")
            except Exception as e:
                print(f"상태 확인 중 오류 발생: {str(e)}")
            
            # 컨테이너 상태 출력
            if container:
                print(f"현재 컨테이너 상태: {container.status}")
            
            time.sleep(2)  # 2초 간격으로 확인
        else:
            raise TimeoutError(
                "RabbitMQ 서버 시작 시간이 초과되었습니다.\n"
                f"마지막 로그: {container.logs().decode('utf-8') if container else 'No logs'}"
            )

        yield container

    except Exception as e:
        print(f"RabbitMQ 컨테이너 설정 중 오류 발생: {str(e)}")
        raise

    finally:
        if container:
            try:
                print("테스트 종료, RabbitMQ 컨테이너를 정리합니다...")
                container.stop()
                container.remove()
                print("RabbitMQ 컨테이너가 성공적으로 정리되었습니다.")
            except Exception as e:
                print(f"컨테이너 정리 중 오류 발생: {str(e)}")

def get_config_path(env: str) -> str:
    """환경에 따른 설정 파일 경로를 반환합니다."""
    # tests/integration/conftest.py -> tests -> .. -> src/config
    config_dir = Path(__file__).parent.parent.parent / "config"
    return str(config_dir / f"{env}.yaml")

@pytest.fixture(scope="session")
def app(rabbitmq_container) -> Generator[Flask, None, None]:
    """테스트용 Flask 애플리케이션 픽스처"""
    app = create_app(config_path=get_config_path("test"))
    
    engine = app.extensions['di_container'].db_engine()
    Base.metadata.create_all(bind=engine)
    
    # 테스트 컨텍스트 설정
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # 테스트 종료 후 정리
    Base.metadata.drop_all(bind=engine)
    ctx.pop()

@pytest.fixture(scope="session")
def test_client(app: Flask):
    """테스트 클라이언트 픽스처"""
    return app.test_client()

@pytest.fixture
def container(app):
    """DI 컨테이너 픽스처"""
    return app.extensions['di_container']

@pytest.fixture
def uow(container):
    """UnitOfWork 픽스처"""
    uow = container.uow()
    yield uow
    # 테스트 후 롤백
    if hasattr(uow, '_session'):
        uow._session.rollback()
        uow._session.close()

@pytest.fixture
def message_bus(container):
    """메시지 버스 픽스처"""
    return container.message_bus()

@pytest.fixture
def password_hasher(container):
    """비밀번호 해셔 픽스처"""
    return container.password_hasher()

@pytest.fixture
def token_generator(container):
    """토큰 생성기 픽스처"""
    return container.token_generator()

@pytest.fixture
def id_generator(container):
    """ID 생성기 픽스처"""
    return container.id_generator()
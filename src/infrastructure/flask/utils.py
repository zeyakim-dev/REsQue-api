from typing import TypeVar, Type, Optional, cast
from flask import current_app
from dependency_injector.providers import Provider

T = TypeVar('T')

class ContainerNotInitializedError(Exception):
    """DI 컨테이너가 초기화되지 않은 경우 발생하는 예외"""
    pass

def get_container():
    """현재 Flask 앱의 DI 컨테이너를 반환합니다."""
    if not current_app:
        raise RuntimeError("Flask 애플리케이션 컨텍스트 외부에서 호출되었습니다")
        
    container = current_app.extensions.get('di_container')
    if not container:
        raise ContainerNotInitializedError("DI 컨테이너가 초기화되지 않았습니다")
        
    return container

def get_provider(provider_type: Type[T]) -> Optional[T]:
    """컨테이너에서 특정 타입의 provider를 가져옵니다."""
    container = get_container()
    provider = getattr(container, provider_type.__name__.lower(), None)
    
    if not provider or not isinstance(provider, Provider):
        return None
        
    return cast(T, provider())
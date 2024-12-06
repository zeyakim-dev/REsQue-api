from typing import Optional
from pathlib import Path
from flask import Flask
from src.bootstrap.bootstrap import Bootstrap

def create_app(config_path: Optional[str] = None) -> Flask:
    """Flask 애플리케이션을 생성합니다.
    
    Args:
        config_path: 설정 파일 경로. None인 경우 기본 경로 사용
        
    Returns:
        Flask: 설정이 완료된 Flask 애플리케이션
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")
        
    bootstrap = Bootstrap(config_path)
    return bootstrap.create_app()
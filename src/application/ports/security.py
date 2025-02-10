from abc import ABC, abstractmethod
from typing import Protocol

class PasswordHasher(Protocol):
    """비밀번호 해시 처리 포트
    
    애플리케이션 계층이 인프라 계층의 해시 처리를 추상화
    """
    
    def hash(self, plain_password: str) -> str:
        """평문 비밀번호를 해시화
        
        Args:
            plain_password: 평문 비밀번호
            
        Returns:
            str: 해시된 비밀번호
        """
        ...
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증
        
        Args:
            plain_password: 검증할 평문 비밀번호
            hashed_password: 저장된 해시 비밀번호
            
        Returns:
            bool: 검증 결과
        """
        ... 
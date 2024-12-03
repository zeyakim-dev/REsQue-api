from dataclasses import dataclass
from typing import Optional
from src.application.commands.command import Command 
from src.application.ports.repositories.user.user_repository import UserRepository
from src.application.ports.uow import UnitOfWork
from src.domain.user.user import User
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator

@dataclass(frozen=True)
class LoginResponse:
    """로그인 응답 데이터입니다."""
    access_token: str
    token_type: str = "Bearer"

@dataclass(frozen=True)
class LoginCommand(Command[LoginResponse]):
    """JWT 토큰을 발급하는 로그인 커맨드입니다."""
    
    username: str
    password: str
    _password_hasher: PasswordHasher
    _token_generator: JWTTokenGenerator
    
    def execute(self, uow: UnitOfWork) -> LoginResponse:
        """로그인을 수행하고 JWT 토큰을 발급합니다.
        
        Args:
            uow: 트랜잭션 관리를 위한 UnitOfWork 인스턴스
            
        Returns:
            LoginResponse: access token을 포함한 로그인 응답
            
        Raises:
            ValueError: 사용자명이 존재하지 않거나 비밀번호가 일치하지 않는 경우
        """
        with uow:
            user_repository: UserRepository = uow.get_repository(UserRepository)
            
            # 사용자 조회 및 비밀번호 검증
            user = user_repository.find_by_username(self.username)
            if not user:
                raise ValueError("사용자명 또는 비밀번호가 올바르지 않습니다")
                
            if not user.verify_password(self.password, self._password_hasher):
                raise ValueError("사용자명 또는 비밀번호가 올바르지 않습니다")
            
            # JWT 토큰 생성
            token_payload = {
                "sub": str(user.id),
                "username": user.username
            }
            access_token = self._token_generator.generate_token(token_payload)
            
            return LoginResponse(access_token=access_token)
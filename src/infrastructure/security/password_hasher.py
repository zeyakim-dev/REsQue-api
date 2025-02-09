import bcrypt
from src.application.ports.security import PasswordHasher

class BcryptPasswordHasher:
    """Bcrypt 기반 비밀번호 해시 처리 구현"""
    
    def __init__(self, rounds: int = 12):
        """
        Args:
            rounds: 해시 라운드 수 (기본값 12)
                   높을수록 보안성은 증가하나 성능은 저하
        """
        self.rounds = rounds
    
    def hash(self, plain_password: str) -> str:
        """비밀번호 해시화
        
        Args:
            plain_password: 평문 비밀번호
            
        Returns:
            str: 해시된 비밀번호 (UTF-8 인코딩)
        """
        # 솔트 자동 생성 및 해시 처리
        password_bytes = plain_password.encode('utf-8')
        hashed = bcrypt.hashpw(
            password=password_bytes,
            salt=bcrypt.gensalt(rounds=self.rounds)
        )
        return hashed.decode('utf-8')
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증
        
        Args:
            plain_password: 검증할 평문 비밀번호
            hashed_password: 저장된 해시 비밀번호
            
        Returns:
            bool: 검증 결과
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        try:
            return bcrypt.checkpw(
                password=password_bytes,
                hashed_password=hashed_bytes
            )
        except ValueError:
            # 잘못된 해시 형식 등의 예외 처리
            return False 
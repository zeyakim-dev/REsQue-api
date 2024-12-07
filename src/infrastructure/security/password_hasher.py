from typing import Optional

import bcrypt

from src.application.ports.security.password_hasher import AbstractPasswordHasher


class PasswordHasher(AbstractPasswordHasher):
    """비밀번호를 안전하게 해시화하는 BCrypt 기반 구현체입니다.
    
    이 클래스는 BCrypt 알고리즘을 사용하여 AbstractPasswordHasher 인터페이스를
    구현합니다. work_factor를 통해 해싱의 강도를 조절할 수 있으며,
    기본값은 12로 설정되어 있습니다.
    """

    def __init__(self, work_factor: int = 12):
        """해시 강도를 설정하여 구현체를 초기화합니다.
        
        Args:
            work_factor: BCrypt의 반복 횟수입니다. 값이 1 증가할 때마다
                        해싱 시간이 2배로 증가합니다. 일반적으로
                        10-14 사이의 값을 권장합니다.
                        
        Raises:
            ValueError: work_factor가 유효한 범위(4-31)를 벗어난 경우
        """
        if not (4 <= work_factor <= 31):
            raise ValueError("work_factor는 4에서 31 사이의 값이어야 합니다")
        self._work_factor = work_factor

    def hash(self, password: str) -> str:
        """AbstractPasswordHasher.hash의 BCrypt 기반 구현입니다.
        
        이 메서드는 주어진 비밀번호를 BCrypt 알고리즘으로 해시화합니다.
        비밀번호는 UTF-8로 인코딩되며, 결과는 문자열로 반환됩니다.
        
        Args:
            password: 해시화할 평문 비밀번호
            
        Returns:
            str: 해시화된 비밀번호 (salt 포함)
            
        Raises:
            ValueError: 비밀번호가 빈 문자열이거나 None인 경우
        """
        if not password:
            raise ValueError("비밀번호는 비어있을 수 없습니다")

        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self._work_factor)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode("utf-8")

    def verify(self, password: str, hashed_password: str) -> bool:
        """AbstractPasswordHasher.verify의 BCrypt 기반 구현입니다.
        
        이 메서드는 평문 비밀번호와 해시된 비밀번호를 안전하게 비교합니다.
        BCrypt의 안전한 비교 함수를 사용하여 타이밍 공격을 방지합니다.
        
        Args:
            password: 검증할 평문 비밀번호
            hashed_password: 저장된 해시 비밀번호
            
        Returns:
            bool: 비밀번호가 일치하면 True, 그렇지 않으면 False
            
        Raises:
            ValueError: 비밀번호나 해시가 빈 값인 경우
        """
        if not password or not hashed_password:
            raise ValueError("비밀번호와 해시값은 비어있을 수 없습니다")

        try:
            password_bytes = password.encode("utf-8")
            hash_bytes = hashed_password.encode("utf-8")
            
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except (ValueError, TypeError):
            return False
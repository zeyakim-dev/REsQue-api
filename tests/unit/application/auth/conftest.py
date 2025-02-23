import pytest
import hashlib
from resque_api.application.ports.security import PasswordHasher


class FakePasswordHasher(PasswordHasher):
    """테스트용 PasswordHasher 구현"""

    def hash(self, password: str) -> str:
        """SHA-256을 사용한 단순 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """해시된 비밀번호와 평문 비밀번호 비교"""
        return self.hash(plain_password) == hashed_password


@pytest.fixture
def hasher():
    """테스트용 PasswordHasher 제공"""
    return FakePasswordHasher()

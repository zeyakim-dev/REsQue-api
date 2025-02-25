import bcrypt

from resque_api.application.ports.security import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Bcrypt 기반 비밀번호 해시 처리 구현"""

    def __init__(self, rounds: int = 12):
        """
        Args:
            rounds: 해시 라운드 수 (기본값 12)
                   높을수록 보안성은 증가하나 성능은 저하
        """
        self.rounds = rounds

    def hash(self, plain_password: str) -> str:
        """비밀번호 해시화"""
        if not plain_password:
            raise ValueError("Password cannot be empty")

        password_bytes = plain_password.encode("utf-8")
        hashed = bcrypt.hashpw(
            password=password_bytes, salt=bcrypt.gensalt(rounds=self.rounds)
        )
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        if not plain_password or not hashed_password:
            return False

        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")

            return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_bytes)
        except (ValueError, TypeError):
            return False

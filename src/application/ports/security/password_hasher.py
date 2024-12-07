from abc import ABC, abstractmethod


class AbstractPasswordHasher(ABC):
    """비밀번호 해싱을 위한 포트입니다.

    이 인터페이스는 비밀번호의 해싱과 검증을 추상화하여,
    애플리케이션이 특정 해싱 알고리즘에 의존하지 않도록 합니다.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """평문 비밀번호를 해시화합니다.

        Args:
            password: 해시화할 평문 비밀번호

        Returns:
            str: 해시화된 비밀번호
        """
        pass

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """해시된 비밀번호와 평문 비밀번호를 비교합니다.

        Args:
            password: 검증할 평문 비밀번호
            hashed_password: 저장된 해시 비밀번호

        Returns:
            bool: 비밀번호가 일치하면 True

        Raises:
            ValueError: 입력값이 유효하지 않은 경우
        """
        pass

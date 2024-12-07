from dataclasses import dataclass

from src.domain.user.exceptions import (
    InvalidPasswordException,
    InvalidUsernameException,
)


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise InvalidUsernameException(self.value, "사용자명은 문자열이어야 합니다")

        if not (4 <= len(self.value) <= 50):
            raise InvalidUsernameException(
                self.value, "사용자명은 최소 3자 이상, 최대 50자 이하여야 합니다"
            )

        if not self.value.isalnum():
            raise InvalidUsernameException(
                self.value, "사용자명은 알파벳과 숫자만 포함할 수 있습니다"
            )


@dataclass(frozen=True)
class HashedPassword:
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidPasswordException(
                "비밀번호는 8자 이상이며, 대소문자와 숫자를 포함해야 합니다"
            )

    def _is_valid(self, value: str) -> bool:
        return True


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidPasswordException(
                "비밀번호는 8자 이상이며, 대소문자와 숫자를 포함해야 합니다"
            )

    def _is_valid(self, value: str) -> bool:
        return (
            isinstance(value, str)
            and len(value) >= 8
            and any(c.isupper() for c in value)
            and any(c.islower() for c in value)
            and any(c.isdigit() for c in value)
        )

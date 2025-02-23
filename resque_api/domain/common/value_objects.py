
from dataclasses import dataclass
import re

from resque_api.domain.base.value_object import ValueObject
from resque_api.domain.common.exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email(ValueObject[str]):
    """이메일 값을 래핑하는 ValueObject"""

    def __post_init__(self):
        """이메일 검증 수행"""
        super().__post_init__()
        self._validate_email()

    def _validate_email(self) -> None:
        """이메일 형식 검증"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise InvalidEmailError(f"Invalid email format: {self.value}")
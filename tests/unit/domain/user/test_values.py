import pytest

from src.domain.user.exceptions import (
    InvalidPasswordException,
    InvalidUsernameException,
)
from src.domain.user.values import Password, Username


class TestUsername:
    def test_valid_username_creation(self):
        """유효한 사용자명으로 Username을 생성할 수 있어야 합니다."""
        username = Username("john123")
        assert username.value == "john123"

    def test_username_must_be_string(self):
        """사용자명은 반드시 문자열이어야 합니다."""
        with pytest.raises(InvalidUsernameException) as exc_info:
            Username(123)
        assert "문자열이어야 합니다" in str(exc_info.value)

    def test_username_length_constraints(self):
        """사용자명은 길이 제한을 준수해야 합니다."""
        # 너무 짧은 경우
        with pytest.raises(InvalidUsernameException) as exc_info:
            Username("abc")
        assert "최소 3자 이상" in str(exc_info.value)

        # 너무 긴 경우
        with pytest.raises(InvalidUsernameException) as exc_info:
            Username("a" * 51)
        assert "최대 50자 이하" in str(exc_info.value)

    def test_username_alphanumeric_only(self):
        """사용자명은 알파벳과 숫자만 포함할 수 있습니다."""
        with pytest.raises(InvalidUsernameException) as exc_info:
            Username("user@name")
        assert "알파벳과 숫자만" in str(exc_info.value)


class TestPassword:
    def test_valid_password_creation(self):
        """유효한 비밀번호로 Password를 생성할 수 있어야 합니다."""
        password = Password("Password123")
        assert password.value == "Password123"

    def test_password_minimum_length(self):
        """비밀번호는 최소 8자 이상이어야 합니다."""
        with pytest.raises(InvalidPasswordException) as exc_info:
            Password("Pass123")
        assert "8자 이상" in str(exc_info.value)

    def test_password_requires_uppercase(self):
        """비밀번호는 대문자를 포함해야 합니다."""
        with pytest.raises(InvalidPasswordException) as exc_info:
            Password("password123")
        assert "대소문자" in str(exc_info.value)

    def test_password_requires_lowercase(self):
        """비밀번호는 소문자를 포함해야 합니다."""
        with pytest.raises(InvalidPasswordException) as exc_info:
            Password("PASSWORD123")
        assert "대소문자" in str(exc_info.value)

    def test_password_requires_digit(self):
        """비밀번호는 숫자를 포함해야 합니다."""
        with pytest.raises(InvalidPasswordException) as exc_info:
            Password("PasswordABC")
        assert "숫자" in str(exc_info.value)

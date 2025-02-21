from datetime import datetime, timezone
from uuid import uuid4

import pytest

from resque_api.domain.user.entities import User
from resque_api.domain.user.exceptions import InactiveUserError, InvalidEmailError
from resque_api.domain.user.value_objects import AuthProvider, Password, UserStatus
from resque_api.infrastructure.security.password_hasher import BcryptPasswordHasher


class TestUser:
    """User 엔티티 테스트

    도메인 규칙:
    - 이메일은 유일한 식별자로 사용됨
    - OAuth 사용자는 별도의 인증 로직 사용
    - 비활성 상태의 사용자는 어떤 작업도 수행할 수 없음
    """

    class TestUserCreation:
        """사용자 생성 테스트"""

        def test_create_user_with_valid_email(self, valid_user_data):
            """이메일 기반 사용자 생성 테스트

            시나리오:
            1. 유효한 이메일로 사용자 생성
            2. 생성된 사용자의 속성 검증
            """
            # When
            user = User(**valid_user_data)

            # Then
            assert user.id == valid_user_data["id"]
            assert user.email == valid_user_data["email"]
            assert user.auth_provider == AuthProvider.EMAIL
            assert user.status == UserStatus.ACTIVE

        def test_create_user_with_invalid_email(self, valid_user_data):
            """잘못된 이메일 형식으로 사용자 생성 시도

            시나리오:
            1. 잘못된 이메일 형식으로 사용자 생성 시도
            2. InvalidEmailError 발생 확인
            """
            # Given
            invalid_data = {**valid_user_data, "email": "invalid-email"}

            # When/Then
            with pytest.raises(InvalidEmailError) as exc_info:
                User(**invalid_data)
            assert "Invalid email format" in str(exc_info.value)

        def test_create_oauth_user(self, valid_user_data):
            """OAuth 사용자 생성 테스트

            시나리오:
            1. Google OAuth 제공자로 사용자 생성
            2. OAuth 관련 속성 검증
            """
            # Given
            oauth_data = {
                **valid_user_data,
                "email": "user@gmail.com",
                "auth_provider": AuthProvider.GOOGLE,
            }

            # When
            user = User(**oauth_data)

            # Then
            assert user.auth_provider == AuthProvider.GOOGLE
            assert "gmail.com" in user.email

    class TestUserAuthentication:
        """사용자 인증 테스트"""

        def test_can_authenticate_email_user(self, valid_user_data):
            """이메일 사용자 인증 가능 여부 테스트"""
            # Given
            user = User(**valid_user_data)

            # When
            can_auth = user.can_authenticate()

            # Then
            assert can_auth is True

        def test_cannot_authenticate_oauth_user(self, valid_user_data):
            """OAuth 사용자 인증 불가능 테스트"""
            # Given
            oauth_user = User(
                **{**valid_user_data, "auth_provider": AuthProvider.GOOGLE}
            )

            # When
            can_auth = oauth_user.can_authenticate()

            # Then
            assert can_auth is False

        def test_cannot_authenticate_inactive_user(self, valid_user_data):
            """비활성 사용자 인증 불가능 테스트"""
            # Given
            inactive_user = User(**{**valid_user_data, "status": UserStatus.INACTIVE})

            # When/Then
            with pytest.raises(InactiveUserError):
                inactive_user.can_authenticate()

    class TestUserStatus:
        """사용자 상태 관리 테스트"""

        def test_deactivate_user(self, valid_user_data):
            """사용자 비활성화 테스트

            시나리오:
            1. 활성 상태의 사용자 생성
            2. 비활성화 상태로 변경
            3. 새로운 User 인스턴스 검증
            """
            # Given
            user = User(**valid_user_data)

            # When
            updated_user = user.update_status(UserStatus.INACTIVE)

            # Then
            assert user.status == UserStatus.ACTIVE  # 원본은 변경되지 않음
            assert updated_user.status == UserStatus.INACTIVE  # 새 인스턴스는 변경됨
            assert updated_user != user  # 다른 객체임을 확인

            # 다른 속성들은 동일한지 확인
            assert updated_user.id == user.id
            assert updated_user.email == user.email
            assert updated_user.auth_provider == user.auth_provider

        def test_inactive_user_operations(self, valid_user_data):
            """비활성 사용자 작업 제한 테스트

            시나리오:
            1. 비활성 상태의 사용자 생성
            2. 각종 작업 시도 시 예외 발생 확인
            """
            # Given
            user = User(**{**valid_user_data, "status": UserStatus.INACTIVE})

            # When/Then
            with pytest.raises(InactiveUserError) as exc_info:
                user.can_authenticate()
            assert "Inactive user cannot perform actions" in str(exc_info.value)

            with pytest.raises(InactiveUserError) as exc_info:
                user.update_status(UserStatus.ACTIVE)
            assert "Inactive user cannot perform actions" in str(exc_info.value)

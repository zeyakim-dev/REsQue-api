import pytest
from datetime import datetime
from uuid import uuid4
from src.domain.user.entities import User
from src.domain.user.value_objects import AuthProvider, UserStatus
from src.domain.user.exceptions import InvalidEmailError, InactiveUserError

class TestUser:
    """User 엔티티 테스트
    
    도메인 규칙:
    - 이메일은 유일한 식별자로 사용됨
    - OAuth 사용자는 별도의 인증 로직 사용
    - 비활성 상태의 사용자는 어떤 작업도 수행할 수 없음
    """
    
    @pytest.fixture
    def valid_user_data(self):
        """기본 테스트용 사용자 데이터"""
        return {
            "id": uuid4(),
            "email": "test@example.com",
            "auth_provider": AuthProvider.EMAIL,
            "status": UserStatus.ACTIVE,
            "created_at": datetime.now(datetime.UTC)
        }

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
                "auth_provider": AuthProvider.GOOGLE
            }
            
            # When
            user = User(**oauth_data)
            
            # Then
            assert user.auth_provider == AuthProvider.GOOGLE
            assert "gmail.com" in user.email

    class TestUserAuthentication:
        """사용자 인증 테스트"""
        
        def test_authenticate_email_user(self, valid_user_data):
            """이메일 사용자 인증 테스트
            
            시나리오:
            1. 이메일 사용자 생성
            2. 올바른 비밀번호로 인증
            """
            # Given
            user = User(**valid_user_data)
            correct_password = "correct_password"
            
            # When
            is_authenticated = user.authenticate(correct_password)
            
            # Then
            assert is_authenticated is True
        
        def test_authenticate_with_wrong_password(self, valid_user_data):
            """잘못된 비밀번호로 인증 시도
            
            시나리오:
            1. 이메일 사용자 생성
            2. 잘못된 비밀번호로 인증 시도
            """
            # Given
            user = User(**valid_user_data)
            wrong_password = "wrong_password"
            
            # When
            is_authenticated = user.authenticate(wrong_password)
            
            # Then
            assert is_authenticated is False

    class TestUserStatus:
        """사용자 상태 관리 테스트"""
        
        def test_deactivate_user(self, valid_user_data):
            """사용자 비활성화 테스트
            
            시나리오:
            1. 활성 상태의 사용자 생성
            2. 비활성화 상태로 변경
            """
            # Given
            user = User(**valid_user_data)
            
            # When
            user.update_status(UserStatus.INACTIVE)
            
            # Then
            assert user.status == UserStatus.INACTIVE
        
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
                user.authenticate("any_password")
            assert "Inactive user cannot perform actions" in str(exc_info.value)
            
            with pytest.raises(InactiveUserError) as exc_info:
                user.update_status(UserStatus.ACTIVE)
            assert "Inactive user cannot perform actions" in str(exc_info.value) 
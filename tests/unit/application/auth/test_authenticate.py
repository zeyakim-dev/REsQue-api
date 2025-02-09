import pytest
from src.application.auth.authenticate import authenticate_user
from src.domain.user.entities import User
from src.domain.user.value_objects import Password

class TestAuthenticate:
    def test_authenticate_user_success(self, valid_user_data, hasher):
        """사용자 인증 성공 테스트"""
        # Given
        user = User(**valid_user_data)
        plain_password = "secure_password123"
        
        # When
        is_authenticated = authenticate_user(user, plain_password, hasher)
        
        # Then
        assert is_authenticated is True
    
    def test_authenticate_with_wrong_password(self, valid_user_data, hasher):
        """잘못된 비밀번호로 인증 실패 테스트"""
        # Given
        user = User(**valid_user_data)
        wrong_password = "wrong_password"
        
        # When
        is_authenticated = authenticate_user(user, wrong_password, hasher)
        
        # Then
        assert is_authenticated is False
    
    def test_authenticate_with_invalid_user(self, hasher):
        """유효하지 않은 사용자로 인증 실패 테스트"""
        # When
        is_authenticated = authenticate_user(None, "any_password", hasher)
        
        # Then
        assert is_authenticated is False 
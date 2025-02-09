import pytest
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

class TestBcryptPasswordHasher:
    """BcryptPasswordHasher 테스트"""
    
    @pytest.fixture
    def hasher(self):
        """테스트용 해셔 인스턴스"""
        return BcryptPasswordHasher(rounds=4)  # 테스트용으로 라운드 수 감소
    
    def test_hash_and_verify(self, hasher):
        """해시 생성 및 검증 테스트
        
        시나리오:
        1. 평문 비밀번호 해시화
        2. 생성된 해시로 검증
        """
        # Given
        password = "secure_password123"
        
        # When
        hashed = hasher.hash(password)
        is_valid = hasher.verify(password, hashed)
        
        # Then
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert is_valid is True
    
    def test_verify_with_wrong_password(self, hasher):
        """잘못된 비밀번호 검증 테스트"""
        # Given
        password = "correct_password"
        wrong_password = "wrong_password"
        
        # When
        hashed = hasher.hash(password)
        is_valid = hasher.verify(wrong_password, hashed)
        
        # Then
        assert is_valid is False
    
    def test_verify_with_invalid_hash(self, hasher):
        """잘못된 해시 형식 검증 테스트"""
        # Given
        password = "any_password"
        invalid_hash = "invalid_hash_format"
        
        # When
        is_valid = hasher.verify(password, invalid_hash)
        
        # Then
        assert is_valid is False
    
    def test_different_rounds_produce_different_hashes(self):
        """라운드 수에 따른 해시 차이 테스트"""
        # Given
        password = "test_password"
        hasher1 = BcryptPasswordHasher(rounds=4)
        hasher2 = BcryptPasswordHasher(rounds=5)
        
        # When
        hash1 = hasher1.hash(password)
        hash2 = hasher2.hash(password)
        
        # Then
        assert hash1 != hash2
        assert hasher1.verify(password, hash1)
        assert hasher2.verify(password, hash2) 
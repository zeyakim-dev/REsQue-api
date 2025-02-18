import pytest
from resque_api.infrastructure.security.password_hasher import BcryptPasswordHasher
import secrets

class TestBcryptPasswordHasher:
    """BcryptPasswordHasher 테스트"""
    
    @pytest.fixture
    def hasher(self):
        """테스트용 해셔 인스턴스"""
        return BcryptPasswordHasher(rounds=4)  # 테스트용으로 라운드 수 감소
    
    @pytest.fixture
    def secure_password(self):
        """안전한 테스트용 비밀번호 생성"""
        password = secrets.token_urlsafe(16)
        yield password
        # 메모리 초기화 시도
        del password
    
    def test_hash_with_empty_password(self, hasher):
        """빈 비밀번호 해시화 시도"""
        with pytest.raises(ValueError) as exc_info:
            hasher.hash("")
        assert "Password cannot be empty" in str(exc_info.value)
    
    def test_verify_with_empty_inputs(self, hasher):
        """빈 입력값으로 검증 시도"""
        assert not hasher.verify("", "")
        assert not hasher.verify("password", "")
        assert not hasher.verify("", "hash")
    
    def test_hash_and_verify(self, hasher, secure_password):
        """해시 생성 및 검증 테스트
        
        시나리오:
        1. 평문 비밀번호 해시화
        2. 생성된 해시로 검증
        """
        # When
        hashed = hasher.hash(secure_password)
        is_valid = hasher.verify(secure_password, hashed)
        
        # Then
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert is_valid is True
        
        # 해시가 bcrypt 형식을 따르는지 검증
        assert hashed.startswith("$2b$")
    
    def test_verify_with_wrong_password(self, hasher, secure_password):
        """잘못된 비밀번호 검증 테스트"""
        # Given
        wrong_password = secrets.token_urlsafe(16)
        
        # When
        hashed = hasher.hash(secure_password)
        is_valid = hasher.verify(wrong_password, hashed)
        
        # Then
        assert is_valid is False
    
    @pytest.mark.parametrize("invalid_hash", [
        "invalid_format",
        "$2b$invalid",
        "한글해시",
        "\x00binary\x00",
        "a" * 1000  # 너무 긴 해시
    ])
    def test_verify_with_invalid_hash(self, hasher, secure_password, invalid_hash):
        """잘못된 해시 형식 검증 테스트"""
        assert not hasher.verify(secure_password, invalid_hash)
    
    def test_different_rounds_produce_different_hashes(self, secure_password):
        """라운드 수에 따른 해시 차이 테스트"""
        # Given
        hasher1 = BcryptPasswordHasher(rounds=4)
        hasher2 = BcryptPasswordHasher(rounds=5)
        
        # When
        hash1 = hasher1.hash(secure_password)
        hash2 = hasher2.hash(secure_password)
        
        # Then
        assert hash1 != hash2
        assert hasher1.verify(secure_password, hash1)
        assert hasher2.verify(secure_password, hash2)
        
        # 라운드 수 검증
        assert hash1.startswith("$2b$04$")
        assert hash2.startswith("$2b$05$") 
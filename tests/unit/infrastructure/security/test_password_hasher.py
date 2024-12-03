import pytest
from pytest_mock import MockerFixture

from src.infrastructure.security.password_hasher import PasswordHasher

class TestPasswordHasher:
    @pytest.fixture
    def mock_bcrypt(self, mocker: MockerFixture):
        """bcrypt의 모든 필요한 함수들을 모킹합니다."""
        # 먼저 전체 bcrypt 모듈을 모킹
        mock_bcrypt = mocker.patch('src.infrastructure.security.password_hasher.bcrypt')
        
        # salt 생성 결과 설정
        mock_bcrypt.gensalt.return_value = b"$2b$04$mockedsalt"
        
        # 해시 결과 설정
        mock_bcrypt.hashpw.return_value = b"$2b$04$mockedsalt.hashedpassword"
        
        return mock_bcrypt

    @pytest.fixture
    def hasher(self) -> PasswordHasher:
        """테스트용 PasswordHasher 인스턴스를 생성합니다."""
        return PasswordHasher(work_factor=4)

    def test_hash_uses_configured_work_factor(
        self,
        hasher: PasswordHasher,
        mock_bcrypt: MockerFixture
    ):
        """work factor가 올바르게 사용되는지 검증합니다."""
        # When: 비밀번호를 해시화할 때
        result = hasher.hash("any_password")

        # Then: gensalt이 올바른 rounds 값으로 호출되어야 함
        mock_bcrypt.gensalt.assert_called_once_with(rounds=4)
        
        # 그리고: hashpw가 올바른 인자들로 호출되어야 함
        mock_bcrypt.hashpw.assert_called_once_with(
            b"any_password",  # 인코딩된 비밀번호
            mock_bcrypt.gensalt.return_value  # 생성된 salt
        )

    def test_hash_encodes_password_correctly(
        self,
        hasher: PasswordHasher,
        mock_bcrypt: MockerFixture
    ):
        """비밀번호가 올바르게 UTF-8로 인코딩되는지 검증합니다."""
        # Given: 한글이 포함된 비밀번호
        password = "테스트비밀번호123"
        
        # When: 해시화를 시도할 때
        hasher.hash(password)
        
        # Then: hashpw에 전달된 첫 번째 인자가 올바르게 인코딩된 bytes여야 함
        called_password = mock_bcrypt.hashpw.call_args[0][0]
        assert called_password == password.encode('utf-8')
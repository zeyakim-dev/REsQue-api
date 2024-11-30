import pytest
from uuid import UUID

from src.domain.user.user import User
from src.application.commands.auth.register_command import RegisterCommand

class TestRegisterCommand:
    @pytest.fixture
    def mock_user_repository(self, mocker):
        return mocker.Mock(spec=['save'])
    
    @pytest.fixture
    def mock_password_hasher(self, mocker):
        hasher = mocker.Mock()
        hasher.hash.return_value = "hashed_password_123"
        return hasher
    
    @pytest.fixture
    def mock_id_generator(self, mocker):
        generator = mocker.Mock()
        generator.generate.return_value = UUID("12345678-1234-5678-1234-567812345678")
        return generator
    
    @pytest.fixture
    def command(self):
        return RegisterCommand(
            username="testuser",
            password="password123"
        )
    
    def test_execute_creates_user_with_correct_data(
        self,
        command: RegisterCommand,
        mock_user_repository,
        mock_password_hasher,
        mock_id_generator
    ):
        # When
        command.execute(mock_user_repository, mock_id_generator, mock_password_hasher)
        
        # Then
        mock_password_hasher.hash.assert_called_once_with("password123")
        mock_id_generator.generate.assert_called_once()
        
        saved_user = mock_user_repository.save.call_args[0][0]
        assert isinstance(saved_user, User)
        assert saved_user.username == "testuser"
        assert saved_user.hashed_password == "hashed_password_123"
        assert saved_user.id == UUID("12345678-1234-5678-1234-567812345678")
    
    def test_execute_with_invalid_data(
        self,
        mock_user_repository,
        mock_password_hasher,
        mock_id_generator,
        mocker
    ):
        # Given
        mocker.patch('src.domain.user.user.User.create', side_effect=ValueError("잘못된 사용자 데이터"))
        command = RegisterCommand(username="", password="")
        
        # When/Then
        with pytest.raises(ValueError, match="잘못된 사용자 데이터"):
            command.execute(mock_user_repository, mock_id_generator, mock_password_hasher)
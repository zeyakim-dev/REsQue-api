from dataclasses import dataclass
from typing import Any, List
from unittest.mock import Mock, call

import pytest

from src.application.commands.command import Command
from src.application.events.event import Event
from src.application.ports.message_bus import AbstractMessageBus, Message
from src.application.ports.uow import UnitOfWork


@dataclass
class FakeCreateUserCommand(Command):
    username: str
    email: str

    def execute(self): ...


@dataclass
class FakeUserCreatedEvent(Event):
    user_id: str
    username: str


class StubMessageBus(AbstractMessageBus):
    """테스트를 위한 MessageBus Stub"""

    def _handle_event(self, event: Event, uow: UnitOfWork) -> None:
        # Stub이므로 아무 동작도 하지 않음
        pass

    def _handle_command(self, command: Command, uow: UnitOfWork) -> Any:
        # 커맨드 처리를 시뮬레이션
        if isinstance(command, FakeCreateUserCommand):
            return {"user_id": "123", "username": command.username}
        return None

    def _collect_new_events(self, uow: UnitOfWork) -> List[Event]:
        return []

    def _publish_event(self, event: Event) -> None:
        """이벤트를 외부 메시지 브로커에 발행합니다."""
        ...

    def _publish_error(self, message: Message, error: Exception) -> None:
        """에러 상황을 외부 메시지 브로커에 발행합니다."""
        ...


class TestAbstractMessageBus:
    @pytest.fixture
    def uow(self):
        return Mock()

    @pytest.fixture
    def message_bus(self):
        return StubMessageBus()

    @pytest.fixture
    def create_user_command(self):
        return FakeCreateUserCommand("testuser", "test@test.com")

    @pytest.fixture
    def user_created_event(self):
        return FakeUserCreatedEvent("123", "testuser")

    def test_command_handling_workflow(
        self, message_bus, uow, create_user_command, user_created_event
    ):
        """커맨드 처리 워크플로우를 테스트합니다."""
        # Arrange
        message_bus._collect_new_events = Mock()
        message_bus._collect_new_events.side_effect = [
            [user_created_event],  # 첫 번째 호출
            [],  # 두 번째 호출 이후
        ]
        message_bus._handle_event = Mock()

        # Act
        results = message_bus.handle(create_user_command, uow)

        # Assert
        assert len(results) == 1
        assert results[0]["username"] == "testuser"
        assert message_bus._handle_event.call_count == 1
        message_bus._handle_event.assert_called_once_with(user_created_event, uow)
        assert message_bus._collect_new_events.call_count == 2
        message_bus._collect_new_events.assert_has_calls([call(uow), call(uow)])

    def test_event_chain_processing(self, message_bus, uow, user_created_event):
        """이벤트 체인 처리를 테스트합니다."""
        # Arrange
        notification_event = FakeUserCreatedEvent(
            "123", "testuser"
        )  # 실제로는 다른 이벤트 타입을 사용해야 함
        message_bus._collect_new_events = Mock(side_effect=[[notification_event], []])
        message_bus._handle_event = Mock()

        # Act
        message_bus.handle(user_created_event, uow)

        # Assert
        message_bus._handle_event.assert_has_calls(
            [call(user_created_event, uow), call(notification_event, uow)]
        )
        assert message_bus._collect_new_events.call_count == 2

    def test_error_handling(self, message_bus, uow):
        """에러 처리를 테스트합니다."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc:
            message_bus._process_message(None, uow)
        assert "Unknown message type" in str(exc.value)

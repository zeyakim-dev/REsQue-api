import pytest
from resque_api.application.message.bus.message_bus import MessageBus
from resque_api.application.message.command.base.command import Command
from resque_api.application.message.event.base.event import Event
from resque_api.application.ports.uow import UnitOfWork
from resque_api.application.message.command.base.command_handler import CommandHandler
from resque_api.application.message.event.base.event_handler import EventHandler


@pytest.fixture
def mock_command_handler(mocker):
    return mocker.create_autospec(CommandHandler, instance=True)

@pytest.fixture
def mock_event_handler(mocker):
    return mocker.create_autospec(EventHandler, instance=True)

@pytest.fixture
def mock_command(mocker):
    return mocker.create_autospec(Command, instance=True)

@pytest.fixture
def mock_event(mocker):
    return mocker.create_autospec(Event, instance=True)

@pytest.fixture
def uow(mocker):
    return mocker.create_autospec(UnitOfWork, instance=True)

@pytest.fixture
def message_bus(uow):
    return MessageBus(uow)

class TestHandlerRegistration:
    def test_register_handler(self, message_bus, mock_command_handler, mock_command):
        message_bus.subscribe(mock_command_handler, type(mock_command))
        assert type(mock_command) in message_bus.handlers
        assert message_bus.handlers[type(mock_command)] == mock_command_handler

    def test_prevent_duplicate_handler_registration(self, message_bus, mock_command_handler, mock_command):
        message_bus.subscribe(mock_command_handler, type(mock_command))
        with pytest.raises(Exception, match="핸들러가 이미 등록되었습니다"):
            message_bus.subscribe(mock_command_handler, type(mock_command))

class TestMessagePublishing:
    def test_publish_valid_command(self, message_bus, mock_command_handler, mock_command):
        message_bus.subscribe(mock_command_handler, type(mock_command))
        message_bus.publish(mock_command)

        mock_command_handler.handle.assert_called_once_with(mock_command, message_bus.uow)

    def test_publish_unregistered_command(self, message_bus, mock_command):
        with pytest.raises(Exception, match="등록된 핸들러가 없습니다"):
            message_bus.publish(mock_command)

class TestEventQueue:
    def test_add_event_to_queue(self, message_bus, mock_event_handler, mock_event, mocker):
        message_bus.subscribe(mock_event_handler, type(mock_event))
        message_bus.uow.pop_events.return_value = [mock_event]

        message_bus.publish(mock_event)

        assert mock_event in message_bus.event_queue

    def test_process_event_queue(self, message_bus, mock_event_handler, mock_event, mocker):
        message_bus.subscribe(mock_event_handler, type(mock_event))
        message_bus.uow.pop_events.return_value = [mock_event]

        message_bus.publish(mock_event)
        message_bus.event_queue.clear()

        assert len(message_bus.event_queue) == 0 
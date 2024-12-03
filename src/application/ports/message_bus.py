from abc import ABC, abstractmethod
from collections import deque
from typing import Any, List
from src.application.commands.command import Command
from src.application.events.event import Event
from src.application.ports.uow import UnitOfWork

Message = Command | Event

class AbstractMessageBus(ABC):
    """메시지 버스의 추상 기본 클래스입니다."""
    
    def handle(self, message: Message, uow: UnitOfWork) -> List[Any]:
        """메시지를 처리하고 결과를 반환합니다."""
        results = []
        queue = deque([message])
        
        while queue:
            current_message = queue.popleft()
            try:
                result = self._process_message(current_message, uow)
                if result is not None:
                    results.append(result)
                    
                # 새 이벤트 수집 및 외부 발행
                new_events = self._collect_new_events(uow)
                for event in new_events:
                    self._publish_event(event)  # 외부 발행용 hook 추가
                queue.extend(new_events)
                    
            except Exception as e:
                self._handle_message_error(current_message, e)
                
        return results

    def _process_message(self, message: Message, uow: UnitOfWork) -> Any:
        """메시지를 처리하고 결과를 반환합니다."""
        if isinstance(message, Command):
            return self._handle_command(message, uow)
        elif isinstance(message, Event):
            self._handle_event(message, uow)
            return None
        raise ValueError(f"Unknown message type: {type(message)}")

    def _handle_message_error(self, message: Message, error: Exception) -> None:
        """메시지 처리 중 발생한 오류를 처리합니다."""
        self._publish_error(message, error)  # 에러 발행용 hook 추가
        raise error

    @abstractmethod
    def _handle_event(self, event: Event, uow: UnitOfWork) -> None:
        """이벤트를 처리합니다."""
        ...

    @abstractmethod
    def _handle_command(self, command: Command, uow: UnitOfWork) -> Any:
        """커맨드를 처리하고 결과를 반환합니다."""
        ...

    @abstractmethod
    def _collect_new_events(self, uow: UnitOfWork) -> List[Event]:
        """UoW에서 새로운 이벤트를 수집합니다."""
        ...

    @abstractmethod
    def _publish_event(self, event: Event) -> None:
        """이벤트를 외부 메시지 브로커에 발행합니다."""
        ...

    @abstractmethod
    def _publish_error(self, message: Message, error: Exception) -> None:
        """에러 상황을 외부 메시지 브로커에 발행합니다."""
        ...
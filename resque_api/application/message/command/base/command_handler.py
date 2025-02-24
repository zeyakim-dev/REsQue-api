from typing import Any, Generic, Protocol, TypeVar

from resque_api.application.message.command.base.command import Command

C = TypeVar('C', bound=Command)

class CommandHandler(Protocol, Generic[C]):
    def execute(self, command: C) -> Any:
        ...
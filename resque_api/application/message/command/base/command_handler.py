from typing import Any, Generic, Protocol, TypeVar

from resque_api.application.message.command.base.command import Command
from resque_api.application.ports.uow import UnitOfWork

C = TypeVar('C', bound=Command)

class CommandHandler(Protocol, Generic[C]):
    def handle(self, command: C, uow: UnitOfWork) -> Any:
        ...
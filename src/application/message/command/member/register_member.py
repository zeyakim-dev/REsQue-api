from dataclasses import dataclass

from src.application.message.command.command import Command


@dataclass(frozen=True)
class RegisterMemberCommand(Command):
    """새로운 사용자를 등록하는 커맨드입니다."""

    username: str
    plain_password: str
    email: str

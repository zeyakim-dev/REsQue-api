from src.application.message.command.member.register_member import RegisterMemberCommand
from src.application.message.event.member.member_registered import MemberRegisteredEvent
from src.application.message.handler.command.command_handler import CommandHandler
from src.application.ports.id.id_generator import IdGenerator
from src.application.ports.repositories.member.member_repository import MemberRepository
from src.application.ports.security.password_hasher import PasswordHasher
from src.application.ports.uow import UnitOfWork
from src.application.validation.validation_context import ValidationContext
from src.domain.member.entity.member import Member
from src.domain.member.exceptions import (
    DuplicateUsernameException,
    DuplicateEmailException
)
from src.domain.member.values import Email, HashedPassword, PlainPassword, Username

class RegisterMemberCommandHandler(CommandHandler[RegisterMemberCommand, str]):
    """회원 가입 기능을 처리하는 핸들러입니다.


    이 핸들러는 새로운 회원의 등록 과정 전체를 관리합니다. DDD와 CQRS 패턴을 따르며,
    회원 가입에 필요한 모든 유효성 검증과 비즈니스 규칙을 적용합니다. 
    
    핵심 처리 과정은 다음과 같습니다:
    1. 입력된 정보(사용자명, 비밀번호, 이메일)의 형식과 규칙 검증
    2. 사용자명과 이메일의 중복 여부 확인
    3. 비밀번호의 안전한 해싱 처리
    4. 새로운 회원 엔티티 생성 및 영구 저장
    5. 회원 가입 완료 이벤트 발행


    이 핸들러는 다음과 같은 상황에서 예외를 발생시킵니다:
    - 사용자명, 비밀번호, 이메일이 형식에 맞지 않는 경우
    - 이미 사용 중인 사용자명이나 이메일인 경우
    - 비밀번호 해싱 과정에서 문제가 발생한 경우


    Example:
        >>> handler = RegisterMemberCommandHandler(
        ...     id_generator=UuidGenerator(),
        ...     password_hasher=BcryptPasswordHasher(),
        ...     validation_context=ValidationContext()
        ... )
        >>> command = RegisterMemberCommand(
        ...     username="john_doe",
        ...     plain_password="SecurePass123!",
        ...     email="john@example.com"
        ... )
        >>> member_id = handler.execute(command, unit_of_work)


    이 핸들러가 발생시키는 모든 이벤트는 Unit of Work를 통해 관리되며,
    트랜잭션 범위 내에서 안전하게 처리됩니다. 이는 회원 가입 프로세스의
    원자성과 일관성을 보장합니다.

    Attributes:
        _id_generator: 새로운 회원의 고유 식별자를 생성하는 컴포넌트입니다.
            멱등성과 고유성이 보장된 ID를 생성해야 합니다.
        _password_hasher: 사용자 비밀번호를 안전하게 해싱하는 컴포넌트입니다.
            단방향 해시 알고리즘을 사용하여 원본 비밀번호를 보호합니다.
    """

    def __init__(self, id_generator: IdGenerator, password_hasher: PasswordHasher):
        self._id_generator = id_generator
        self._password_hasher = password_hasher
    
    def execute(self, command: RegisterMemberCommand, uow: UnitOfWork) -> str:
        """회원 가입 커맨드를 실행합니다.

        주어진 커맨드를 처리하여 새로운 회원을 등록하고, 등록된 회원의 ID를 반환합니다.

        Args:
            command (RegisterMemberCommand): 회원 가입에 필요한 정보를 담은 커맨드 객체
            uow (UnitOfWork): 트랜잭션 처리를 위한 Unit of Work 객체

        Returns:
            str: 생성된 회원의 고유 식별자

        Raises:
            DuplicateUsernameException: 이미 사용 중인 사용자명인 경우
            DuplicateEmailException: 이미 등록된 이메일 주소인 경우
        """
        self.validate_command(command)        

        with uow:        
            username = Username(command.username)
            plain_password = PlainPassword(command.plain_password)
            email = Email(command.email)

            member_repository = uow.get_repository(MemberRepository)

            # 2. 비즈니스 규칙 검증 - 중복 체크
            if member_repository.exists_by_username(username.value):
                raise DuplicateUsernameException(username.value)
            
            if member_repository.exists_by_email(email.value):
                raise DuplicateEmailException(email.value)

            hashed_password = HashedPassword(
                self._password_hasher.hash(plain_password)
            )

            member_id = self._id_generator.generate()
            new_member = Member(
                id=member_id,
                username=username,
                hashed_password=hashed_password,
                email=email
            )
            
            member_repository.save(new_member)
            
            member_registered_event = MemberRegisteredEvent(new_member.id)
            uow.add_event(member_registered_event)
            
            return new_member.id

    def _validate_command(self, command: RegisterMemberCommand, context: ValidationContext) -> None:
        Username.validate(context, command.username)
        PlainPassword.validate(context, command.plain_password)
        Email.validate(context, command.email)
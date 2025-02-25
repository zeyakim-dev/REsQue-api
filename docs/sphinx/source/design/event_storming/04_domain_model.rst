===========
도메인 모델
===========

사용자 도메인
------------

User
^^^^
.. code-block:: python

    @dataclass
    class User:
        id: UUID
        email: str
        auth_provider: AuthProvider  # EMAIL, GOOGLE
        status: UserStatus  # ACTIVE, INACTIVE
        created_at: datetime

        def authenticate(self, password: str) -> bool:
            """이메일 사용자 인증"""
            pass

        def update_status(self, new_status: UserStatus) -> None:
            """사용자 상태 변경"""
            pass

프로젝트 도메인
-------------

Project
^^^^^^^
.. code-block:: python

    @dataclass
    class Project:
        id: UUID
        title: str
        description: str
        status: ProjectStatus  # ACTIVE, ARCHIVED
        created_at: datetime
        members: List[ProjectMember]
        invitations: List[ProjectInvitation]

        def add_member(self, user: User, role: ProjectRole) -> None:
            """멤버 추가"""
            pass

        def update_status(self, new_status: ProjectStatus) -> None:
            """프로젝트 상태 변경"""
            pass

        def can_modify(self, user: User) -> bool:
            """사용자의 수정 권한 확인"""
            pass

        def invite_member(self, email: str, role: ProjectRole) -> ProjectInvitation:
            """멤버 초대"""
            invitation = ProjectInvitation(
                id=uuid4(),
                project_id=self.id,
                email=email,
                role=role,
                status=InvitationStatus.PENDING,
                expires_at=datetime.utcnow() + timedelta(days=7),
                created_at=datetime.utcnow()
            )
            self.invitations.append(invitation)
            return invitation

ProjectMember
^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class ProjectMember:
        project_id: UUID
        user_id: UUID
        role: ProjectRole  # VIEWER, MEMBER
        joined_at: datetime

        def change_role(self, new_role: ProjectRole) -> None:
            """역할 변경"""
            pass

ProjectInvitation
^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class ProjectInvitation:
        id: UUID
        project_id: UUID
        email: str
        role: ProjectRole
        status: InvitationStatus  # PENDING, ACCEPTED, EXPIRED
        expires_at: datetime
        created_at: datetime

        def accept(self) -> None:
            """초대 수락"""
            if self.is_expired():
                raise InvitationExpiredError()
            self.status = InvitationStatus.ACCEPTED

        def is_expired(self) -> bool:
            """만료 여부 확인"""
            return datetime.utcnow() > self.expires_at

요구사항 도메인
-------------

Requirement
^^^^^^^^^^
.. code-block:: python

    @dataclass
    class Requirement:
        id: UUID
        project_id: UUID
        title: str
        description: str
        status: RequirementStatus  # TODO, IN_PROGRESS, DONE
        assignee_id: Optional[UUID]
        created_at: datetime
        updated_at: datetime
        priority: int
        tags: List[str]
        comments: List[RequirementComment]
        dependencies: List[UUID]

        def assign_to(self, user: User) -> None:
            """담당자 지정"""
            self.assignee_id = user.id

        def change_status(self, new_status: RequirementStatus) -> None:
            """상태 변경"""
            self.status = new_status
            self.updated_at = datetime.utcnow()

        def add_tag(self, tag: str) -> None:
            """태그 추가"""
            if tag not in self.tags:
                self.tags.append(tag)

        def add_comment(self, author: User, content: str) -> None:
            """코멘트 추가"""
            comment = RequirementComment(
                id=uuid4(),
                requirement_id=self.id,
                author_id=author.id,
                content=content,
                created_at=datetime.utcnow()
            )
            self.comments.append(comment)

        def set_priority(self, priority: int) -> None:
            """우선순위 변경"""
            self.priority = priority

RequirementComment
^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class RequirementComment:
        id: UUID
        requirement_id: UUID
        author_id: UUID
        content: str
        created_at: datetime

도메인 규칙
----------

사용자(User)
^^^^^^^^^^^
* 이메일은 유일한 식별자로 사용됨
* OAuth 사용자는 별도의 인증 로직 사용
* 비활성 상태의 사용자는 어떤 작업도 수행할 수 없음

프로젝트(Project)
^^^^^^^^^^^^^^^
* 프로젝트는 반드시 1명 이상의 멤버를 가져야 함
* 프로젝트 생성자는 자동으로 MANAGER 권한을 가짐
* ARCHIVED 상태에서는 모든 수정 작업이 제한됨
* 권한별 가능한 작업:
    - VIEWER: 읽기만 가능
    - MEMBER: 요구사항 생성/수정 가능
    - MANAGER: 프로젝트 설정 변경, 멤버 관리 가능
* 초대 관련 규칙:
    - MANAGER 권한을 가진 멤버만 초대 가능
    - 초대는 7일 후 자동 만료
    - 이미 멤버인 이메일로는 초대 불가
    - 대기 중인 초대가 있는 이메일로는 중복 초대 불가

요구사항(Requirement)
^^^^^^^^^^^^^^^^^^
* 프로젝트에 속한 멤버만 담당자로 지정 가능
* 상태 변경 시 자동으로 updated_at 갱신
* 요구사항은 담당자 없이도 생성 가능
* 우선순위는 정수 값으로 관리됨
* 태그는 중복 없이 관리됨
* 요구사항 간 선행 관계를 지원

값 객체(Value Objects)
-------------------

.. code-block:: python

    class AuthProvider(Enum):
        EMAIL = "EMAIL"
        GOOGLE = "GOOGLE"

    class UserStatus(Enum):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    class ProjectStatus(Enum):
        ACTIVE = "ACTIVE"
        ARCHIVED = "ARCHIVED"

    class ProjectRole(Enum):
        VIEWER = "VIEWER"
        MEMBER = "MEMBER"
        MANAGER = "MANAGER"

    class RequirementStatus(Enum):
        TODO = "TODO"
        IN_PROGRESS = "IN_PROGRESS"
        DONE = "DONE"

    class InvitationStatus(Enum):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        EXPIRED = "EXPIRED"

    class InvitationExpiredError(Exception):
        pass


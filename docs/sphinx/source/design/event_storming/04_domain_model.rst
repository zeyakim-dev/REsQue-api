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
        
        def add_member(self, user: User, role: ProjectRole) -> None:
            """멤버 추가"""
            pass
            
        def update_status(self, new_status: ProjectStatus) -> None:
            """프로젝트 상태 변경"""
            pass
            
        def can_modify(self, user: User) -> bool:
            """사용자의 수정 권한 확인"""
            pass

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
        
        def assign_to(self, user: User) -> None:
            """담당자 지정"""
            pass
            
        def change_status(self, new_status: RequirementStatus) -> None:
            """상태 변경"""
            pass

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

요구사항(Requirement)
^^^^^^^^^^^^^^^^^^
* 프로젝트에 속한 멤버만 담당자로 지정 가능
* 상태 변경 시 자동으로 updated_at 갱신
* 요구사항은 담당자 없이도 생성 가능

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
        VIEWER = "VIEWER"    # 읽기 전용
        MEMBER = "MEMBER"    # 작업 수정 가능
        MANAGER = "MANAGER"  # 프로젝트 관리 권한

    class RequirementStatus(Enum):
        TODO = "TODO"
        IN_PROGRESS = "IN_PROGRESS"
        DONE = "DONE" 
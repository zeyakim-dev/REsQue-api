=================================
커맨드와 쿼리
=================================

커맨드
-----------------

사용자 커맨드
^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class RegisterUser:
        email: str
        password: str

    @dataclass
    class UpdateUserStatus:
        user_id: UUID
        status: UserStatus

프로젝트 커맨드
^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class CreateProject:
        title: str
        description: str
        owner_id: UUID

    @dataclass
    class InviteMember:
        project_id: UUID
        email: str
        role: ProjectRole
        inviter_id: UUID

    @dataclass
    class AcceptInvitation:
        invitation_id: UUID
        user_id: UUID

요구사항 커맨드
^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class CreateRequirement:
        project_id: UUID
        title: str
        description: str
        creator_id: UUID

    @dataclass
    class UpdateRequirementStatus:
        requirement_id: UUID
        status: RequirementStatus
        updater_id: UUID

쿼리
-----------------

사용자 쿼리
^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class GetUserByEmail:
        email: str

    @dataclass
    class GetUserById:
        user_id: UUID

프로젝트 쿼리
^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class GetProjectById:
        project_id: UUID

    @dataclass
    class GetUserProjects:
        user_id: UUID

    @dataclass
    class GetProjectInvitation:
        invitation_id: UUID

    @dataclass
    class GetPendingInvitations:
        email: str

요구사항 쿼리
^^^^^^^^^^^^^^^^^^
.. code-block:: python

    @dataclass
    class GetProjectRequirements:
        project_id: UUID

    @dataclass
    class GetRequirementById:
        requirement_id: UUID 
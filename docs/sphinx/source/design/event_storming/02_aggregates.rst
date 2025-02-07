===================
애그리게이트 정의
===================

회원 애그리게이트
-----------------

UserAggregate
^^^^^^^^^^^^^
:책임:
    * 회원 생명주기 관리(가입/로그인)
    * 계정 상태 관리

:주요 속성:
    .. code-block:: python

        class User:
            id: UUID
            email: str
            auth_provider: AuthProvider  # EMAIL/GOOGLE
            status: UserStatus  # ACTIVE/INACTIVE
            workspace: WorkspaceConfig

:관련 이벤트:
    * 회원_가입됨
    * 회원_로그인됨

프로젝트 애그리게이트
---------------------

ProjectAggregate
^^^^^^^^^^^^^^^^
:책임:
    * 프로젝트 기본 관리
    * 멤버 권한 관리
    * 초대 관리

:주요 속성:
    .. code-block:: python

        class Project:
            id: UUID
            title: str
            owner: UserId
            members: Dict[UserId, ProjectRole]  # viewer/member/manager
            status: ProjectLifecycle  # ACTIVE/ARCHIVED
            invitations: Dict[str, ProjectInvitation]  # 초대 코드: 초대 정보

        class ProjectInvitation:
            code: str  # 유니크한 초대 코드
            email: str  # 초대된 이메일
            role: ProjectRole  # 부여될 권한
            inviter: UserId  # 초대한 사람
            expires_at: datetime  # 만료 시간
            status: InvitationStatus  # PENDING/ACCEPTED/EXPIRED

:관련 이벤트:
    * 프로젝트_생성됨
    * 프로젝트-참여자_추가됨
    * 프로젝트-초대장_발송됨
    * 프로젝트-초대_수락됨
    * 프로젝트-초대_만료됨

요구사항 애그리게이트
---------------------

RequirementAggregate
^^^^^^^^^^^^^^^^^^^^
:책임:
    * 요구사항 기본 CRUD
    * 상태 관리

:주요 속성:
    .. code-block:: python

        class Requirement:
            id: UUID
            title: str
            description: str
            status: RequirementStatus  # TODO/IN_PROGRESS/DONE
            assignee: UserId

:관련 이벤트:
    * 요구사항_등록됨
    * 요구사항_상태_변경됨

협업 애그리게이트
-----------------

CollaborationAggregate
^^^^^^^^^^^^^^^^^^^^^^
:책임:
    * 실시간 알림 배포 시스템
    * 댓글-멘션 연동 처리
    * 알림 전송 실패 복구

:주요 속성:
    .. code-block:: python

        class Notification:
            id: UUID
            channels: List[NotificationChannel]  # EMAIL/SLACK/WEBHOOK
            retry_count: int
            delivery_status: DeliveryState
            user_preferences: Dict[UserId, ChannelConfig]

:관련 이벤트:
    * 알림_전송됨
    * 작업_댓글_추가됨
    * 요구사항-상태_변경됨 → 상태 변경 알림 처리
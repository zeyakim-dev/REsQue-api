===================
애그리게이트 정의
===================

회원 애그리게이트
-----------------

UserAggregate
^^^^^^^^^^^^^
:책임:
    * 회원 생명주기 관리(가입/로그인/탈퇴)
    * 접속 이력 추적
    * 계정 상태 관리

:주요 속성:
    .. code-block:: python

        class User:
            id: UUID
            email: str
            auth_provider: AuthProvider  # EMAIL/GOOGLE/GITHUB
            last_active: datetime
            status: UserStatus  # ACTIVE/INACTIVE/SOFT_DELETED
            workspace: WorkspaceConfig

:관련 이벤트:
    * 회원_가입됨
    * 회원_로그인됨 
    * 회원_탈퇴됨
    * 프로젝트-참여자_추가됨 → workspace 프로젝트 목록 갱신

프로젝트 애그리게이트
---------------------

ProjectAggregate
^^^^^^^^^^^^^^^^
:책임:
    * 프로젝트 전체 생명주기 관리
    * 멤버 권한 계층 관리
    * 참여자 초대 워크플로우

:주요 속성:
    .. code-block:: python

        class Project:
            id: UUID
            title: str
            owner: UserId
            members: Dict[UserId, ProjectRole]  # viewer/member/manager
            status: ProjectLifecycle  # ACTIVE/ARCHIVED/TERMINATED
            invitation_links: List[InvitationToken]
            audit_log: List[PermissionChange]

:관련 이벤트:
    * 프로젝트_생성됨
    * 프로젝트-참여자_추가됨
    * 프로젝트-권한_변경됨
    * 프로젝트_종료됨 → 관련 알림 배치 전송

요구사항 애그리게이트
---------------------

RequirementAggregate
^^^^^^^^^^^^^^^^^^^^
:책임:
    * 요구사항 의존성 그래프 관리
    * 상태 머신 운영
    * 완료 조건 검증

:주요 속성:
    .. code-block:: python

        class Requirement:
            id: UUID
            dependencies: List[RequirementId]
            status_flow: StateMachine
            assignee: UserId
            completion_conditions: CompletionPolicy
            timeline: List[StatusTransition]

:관련 이벤트:
    * 요구사항_등록됨
    * 요구사항-선행조건_연결됨
    * 요구사항_상태_변경됨
    * 요구사항_완료됨

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
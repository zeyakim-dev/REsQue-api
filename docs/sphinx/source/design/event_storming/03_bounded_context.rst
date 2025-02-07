===================
바운디드 컨텍스트
===================

인증/계정 컨텍스트
-----------------

:주요 기능:
    * 회원 가입/로그인 처리
    * 세션 관리
    * Google OAuth 연동

:기술 스택:
    * Flask + Flask-Login
    * Flask-SQLAlchemy (PostgreSQL)
    * Flask-Session (Redis)
    * Flask-OAuthlib (Google OAuth)

:외부 통합:
    * Google OAuth API

프로젝트 관리 컨텍스트
---------------------

:주요 기능:
    * 프로젝트 CRUD
    * 멤버 권한 관리
    * 이메일 초대 관리

:기술 스택:
    * Flask
    * Flask-SQLAlchemy (PostgreSQL)
    * Flask-Caching (Redis)
    * Flask-Mail (이메일 발송)
    * Flask-Marshmallow (직렬화)

:외부 의존성:
    * 인증 컨텍스트 (사용자 정보)
    * SMTP 서버 (이메일 발송)

요구사항 관리 컨텍스트
---------------------

:주요 기능:
    * 요구사항 CRUD
    * 상태 관리 (TODO/IN_PROGRESS/DONE)
    * 담당자 지정

:기술 스택:
    * Flask
    * Flask-SQLAlchemy (PostgreSQL)
    * Flask-Caching (Redis)
    * Flask-Marshmallow (직렬화)

:외부 의존성:
    * 인증 컨텍스트 (사용자 정보)
    * 프로젝트 컨텍스트 (프로젝트 정보)

컨텍스트 간 통신
---------------

:동기 통신:
    * Flask Blueprint 간 직접 호출
    * 공통 모듈을 통한 컨텍스트 간 통신

:데이터 정합성:
    * SQLAlchemy 세션 관리
    * 트랜잭션 범위는 각 컨텍스트 내부로 제한 
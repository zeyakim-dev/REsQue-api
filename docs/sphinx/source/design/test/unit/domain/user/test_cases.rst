===================
User 도메인 테스트
===================

TestUserCreation
---------------

test_create_user_with_valid_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * UUID 생성
    * 유효한 이메일 준비
    * AuthProvider.EMAIL 설정
    * UserStatus.ACTIVE 설정
    * 현재 시간 준비

:Act:
    * User 엔티티 생성

:Assert:
    * id가 일치하는지 확인
    * email이 일치하는지 확인
    * auth_provider가 EMAIL인지 확인
    * status가 ACTIVE인지 확인

test_create_user_with_invalid_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * 잘못된 형식의 이메일 준비
    * 기타 필수 속성 준비

:Act:
    * User 엔티티 생성 시도

:Assert:
    * InvalidEmailError 예외 발생 확인
    * 에러 메시지 검증

test_create_oauth_user
^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * UUID 생성
    * Gmail 이메일 준비
    * AuthProvider.GOOGLE 설정
    * UserStatus.ACTIVE 설정

:Act:
    * User 엔티티 생성

:Assert:
    * auth_provider가 GOOGLE인지 확인
    * email 도메인이 gmail.com인지 확인

TestUserAuthentication
--------------------

test_authenticate_email_user
^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * 이메일 사용자 생성
    * 올바른 비밀번호 해시 준비

:Act:
    * authenticate() 메서드 호출

:Assert:
    * 인증 성공 여부 확인

test_authenticate_oauth_user
^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * OAuth 사용자 생성
    * 유효한 OAuth 토큰 준비

:Act:
    * authenticate() 메서드 호출

:Assert:
    * OAuth 인증 성공 여부 확인

TestUserStatus
------------

test_deactivate_user
^^^^^^^^^^^^^^^^^^
:Arrange:
    * ACTIVE 상태의 사용자 생성

:Act:
    * update_status(UserStatus.INACTIVE) 호출

:Assert:
    * status가 INACTIVE로 변경되었는지 확인

test_inactive_user_operations
^^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * INACTIVE 상태의 사용자 생성

:Act:
    * 각종 작업 수행 시도

:Assert:
    * 모든 작업에서 적절한 예외가 발생하는지 확인

test_duplicate_email_registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:Arrange:
    * 기존 사용자 생성
    * 동일한 이메일로 새 사용자 데이터 준비

:Act:
    * 동일 이메일로 사용자 생성 시도

:Assert:
    * DuplicateEmailError 발생 확인

test_user_withdrawal
^^^^^^^^^^^^^^^^
:Arrange:
    * 활성 상태의 사용자 생성
    * 사용자의 프로젝트 참여 정보 생성

:Act:
    * withdraw() 메서드 호출

:Assert:
    * status가 INACTIVE로 변경
    * 프로젝트 목록에서 제외 확인
    * 이벤트 발생 확인 
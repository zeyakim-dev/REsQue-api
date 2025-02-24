=====================
Requirement 도메인 테스트
=====================

TestRequirement
---------------

요구사항 생성 테스트 (TestRequirementCreation)

요구사항 생성 (test_create_valid_requirement)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 유효한 입력 값으로 요구사항 생성
    * 생성된 요구사항의 속성 검증

:검증 항목:
    * id가 생성됨
    * title과 description이 일치
    * status가 TODO
    * assignee_id는 None (초기 생성 시 담당자 없음)
    * created_at과 updated_at이 설정됨

잘못된 입력으로 요구사항 생성 실패 (test_create_with_invalid_title)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 제목이 비어 있는 요구사항 생성 시도

:검증 항목:
    * RequirementTitleLengthError 예외 발생
    * 적절한 에러 메시지 포함

요구사항 상태 변경 테스트 (TestRequirementStatusTransitions)

상태 변경 성공 (test_valid_status_transition)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항 상태를 TODO에서 IN_PROGRESS 또는 DONE으로 변경

:검증 항목:
    * status가 변경됨
    * updated_at이 갱신됨

잘못된 상태 변경 시도 (test_invalid_transition_from_done)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * DONE 상태의 요구사항을 TODO로 변경 시도

:검증 항목:
    * InvalidStatusTransitionError 예외 발생
    * 적절한 에러 메시지 포함

요구사항 우선순위 변경 테스트 (TestRequirementPriority)

우선순위 변경 (test_set_valid_priority)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항의 우선순위를 1, 2, 3으로 변경

:검증 항목:
    * 우선순위가 정상적으로 변경됨

잘못된 우선순위 변경 (test_invalid_priority_value)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 우선순위를 0 또는 4로 변경 시도

:검증 항목:
    * RequirementPriorityError 예외 발생

요구사항 태그 관리 테스트 (TestRequirementTags)

태그 추가 및 제거 (test_add_and_remove_tags)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항에 태그 추가 및 제거

:검증 항목:
    * 태그가 정상적으로 추가 및 제거됨

요구사항 코멘트 관리 테스트 (TestRequirementComments)

코멘트 추가 (test_add_comment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 사용자에 의해 요구사항에 코멘트 추가

:검증 항목:
    * 코멘트가 정상적으로 추가됨

코멘트 수정 (test_edit_comment_content)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 기존 코멘트 내용을 수정

:검증 항목:
    * 수정된 내용이 반영됨

요구사항 담당자 변경 테스트 (TestRequirementAssignee)

담당자 변경 (test_change_assignee)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 프로젝트 멤버를 담당자로 지정

:검증 항목:
    * assignee_id가 변경됨
    * updated_at이 갱신됨

담당자 해제 (test_unassign_assignee)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 기존 담당자를 제거

:검증 항목:
    * assignee_id가 None으로 변경됨

요구사항 선행조건 연결 테스트 (TestRequirementDependencies)

선행 요구사항 연결 (test_link_valid_predecessor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항을 다른 요구사항의 선행조건으로 연결

:검증 항목:
    * 선행 요구사항이 정상적으로 추가됨

중복 선행 요구사항 방지 (test_prevent_duplicate_predecessor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 동일한 선행 요구사항을 두 번 추가 시도

:검증 항목:
    * 중복 추가되지 않음

순환 의존성 감지 (test_detect_immediate_cycle)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항이 자기 자신을 선행 요구사항으로 추가 시도

:검증 항목:
    * DependencyCycleError 예외 발생

간접 순환 의존성 감지 (test_detect_indirect_cycle)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 다단계 선행 요구사항을 통해 순환 의존성 발생 시도

:검증 항목:
    * DependencyCycleError 예외 발생

유효한 선행조건 제거 (test_unlink_valid_predecessor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:시나리오:
    * 요구사항의 기존 선행 요구사항을 제거

:검증 항목:
    * 요구사항이 정상적으로 제거됨

테스트 설계 원칙
--------------

책임 분리
^^^^^^^^
* 생성: 객체 생성과 유효성 검증
* 상태: 상태 변경 및 우선순위 관리
* 수정: 속성 변경과 담당자 변경
* 삭제: 요구사항 삭제
* 관계: 태그와 선행조건 연결

테스트 격리
^^^^^^^^^
* fixture를 통한 독립적 테스트 데이터 생성
* 각 테스트는 독립적으로 실행 가능

테스트 가독성
^^^^^^^^^^^
* Given-When-Then 패턴 사용
* 명확한 시나리오 문서화
* 검증 항목 명시
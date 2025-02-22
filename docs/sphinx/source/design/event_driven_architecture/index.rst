Event-Driven Architecture
=========================

.. toctree::
   :maxdepth: 1
   :caption: 주요 섹션:
   
   01_overview
   02_core_concepts
   03_components
   04_workflows
   05_examples

Quick Navigation
----------------
- :ref:`개념 이해 <concepts>`
- :ref:`구성 요소 <components>`
- :ref:`실제 구현 예제 <examples>`

.. _overview:

아키텍처 개요
=============

### 프로젝트에서 EDA 적용 배경
우리 프로젝트에서는 기존의 동기식 서비스 호출 방식에서 **이벤트 기반 아키텍처(Event-Driven Architecture, EDA)**로 전환함으로써 **확장성, 장애 격리, 비동기 처리** 등의 이점을 극대화하고자 합니다. 이를 통해 다음과 같은 개선이 기대됩니다:

- 서비스 간 결합도를 낮추어 독립적인 배포 및 확장이 가능
- 비동기 메시징을 활용하여 성능 최적화 및 시스템 부하 감소
- 이벤트 소싱을 통한 변경 이력 관리 및 감사(Audit) 가능

아래는 프로젝트에서 적용할 주요 이벤트 흐름을 나타낸 다이어그램입니다:

.. mermaid::

   flowchart LR
       A[사용자] -->|요구사항 생성| B[CreateRequirementCommand]
       B -->|이벤트 발행| C[RequirementCreatedEvent]
       C --> D[요구사항 조회 모델 업데이트]
       C --> E[알림 서비스 전송]
       D -->|조회| F[사용자]


.. _concepts:

핵심 개념
---------
.. glossary::

   Event Sourcing
      모든 상태 변경을 이벤트 시퀀스로 저장하는 패턴

   CQRS
      명령(쓰기)과 조회(읽기) 모델을 분리하여 독립적으로 확장 가능하도록 하는 패턴.
      이벤트 소싱과 결합할 경우 비동기 메시징을 활용하여 높은 확장성과 성능 최적화를 가능하게 함.

   Eventual Consistency
      데이터 일관성이 시간적 지연 후 달성되는 모델


.. _components:

아키텍처 구성 요소
---------------------------
.. list-table:: 프로젝트에서 사용하는 주요 구성 요소
   :header-rows: 1
   
   * - 구성 요소
     - 역할
     - 예시
   * - Command Bus
     - 명령 라우팅 및 실행
     - CreateRequirementCommand
   * - Event Bus
     - 이벤트 배포 및 전달
     - RequirementCreatedEvent
   * - Event Store
     - 이벤트 저장소 및 감사 로그 관리
     - Kafka / Event Store DB
   * - Saga
     - 분산 트랜잭션 관리
     - RequirementApprovalSaga


.. _workflows_index:

워크플로우
---------------------------
프로젝트에서의 주요 이벤트 흐름을 정의합니다.

### **요구사항(Requirement) 생성 및 변경 흐름**
1. 사용자가 새로운 요구사항을 생성하면 ``CreateRequirementCommand``가 실행됩니다.
2. 요구사항 서비스는 검증 후 ``RequirementCreatedEvent``를 발행합니다.
3. 해당 이벤트를 구독하는 서비스들이 적절한 작업을 수행합니다:
   - 요구사항 조회 모델 업데이트
   - 알림 서비스로 사용자에게 변경 사항 전달
   - 감사 로그에 기록
4. 이후 ``RequirementUpdatedEvent``가 발생하면 동일한 방식으로 처리됩니다.


References
-----------
- `마틴 파울러 이벤트 소싱 <https://martinfowler.com/eaaDev/EventSourcing.html>`_
- `Microsoft EDA 가이드 <https://docs.microsoft.com/ko-kr/azure/architecture/guide/architecture-styles/event-driven>`_


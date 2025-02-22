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

.. _concepts:

Key Concepts
------------
.. glossary::

   Event Sourcing
      모든 상태 변경을 이벤트 시퀀스로 저장하는 패턴

   CQRS
      명령(쓰기)과 조회(읽기) 모델을 분리하여 독립적으로 확장 가능하도록 하는 패턴. 
      이벤트 소싱과 결합할 경우 비동기 메시징을 활용하여 높은 확장성과 성능 최적화를 가능하게 함.

   Eventual Consistency
      데이터 일관성이 시간적 지연 후 달성되는 모델

.. _components:

Architecture Components
---------------------------
.. list-table:: 아키텍처 구성 요소
   :header-rows: 1
   
   * - 구성 요소
     - 역할
     - 예시
   * - Command Bus
     - 명령 라우팅
     - CreateRequirementCommand
   * - Event Bus
     - 이벤트 배포
     - RequirementUpdatedEvent
   * - Saga
     - 분산 트랜잭션 관리
     - OrderProcessingSaga

.. _workflows_index:

Workflows
---------------------------
이벤트 기반 아키텍처에서는 다양한 이벤트 흐름이 존재하며, 이를 통해 시스템 내의 비즈니스 프로세스를 자동화할 수 있습니다. 

예를 들어, **주문 처리(Order Processing)** 흐름을 보면 다음과 같은 이벤트가 발생할 수 있습니다:

1. 사용자가 주문을 생성하면 ``OrderCreatedEvent``가 발생합니다.
2. 결제 서비스가 ``OrderCreatedEvent``를 구독하고 결제를 시도합니다.
3. 결제가 완료되면 ``PaymentCompletedEvent``가 발행됩니다.
4. 주문 처리 서비스가 ``PaymentCompletedEvent``를 받아 배송을 준비합니다.
5. 배송이 시작되면 ``OrderShippedEvent``가 발생하고 고객에게 알림이 전송됩니다.

이러한 방식으로 각 서비스는 독립적으로 동작하며, 이벤트를 통해 상태를 전달하고 관리합니다.

References
-----------
- `마틴 파울러 이벤트 소싱 <https://martinfowler.com/eaaDev/EventSourcing.html>`_
- `Microsoft EDA 가이드 <https://docs.microsoft.com/ko-kr/azure/architecture/guide/architecture-styles/event-driven>`_


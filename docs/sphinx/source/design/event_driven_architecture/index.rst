Event-Driven Architecture (초기 설계 문서)
==========================================

.. toctree::
   :maxdepth: 1
   :caption: 주요 섹션:

   core_concepts
   components
   workflows

개요
-----
이 문서는 제 프로젝트에 적용할 이벤트 기반 아키텍처(EDA)의 초기 설계 방향을 제시합니다.
주요 목표는 서비스 간 결합도 감소, 확장성 확보, 장애 격리 및 비동기 처리를 통한 시스템 성능 최적화입니다.
현재는 기본 개념과 구성 요소, 그리고 간단한 워크플로우만 정의하며,
추후 구현 예제와 상세 설계 내용은 단계별로 보완할 예정입니다.

핵심 개념
---------
본 설계에서 고려하는 핵심 개념은 다음과 같습니다.

- **Event Sourcing**  
  모든 상태 변경을 이벤트로 기록하여 변경 이력 관리와 감사(Audit)를 가능하게 하는 패턴.

- **CQRS (Command Query Responsibility Segregation)**  
  명령(쓰기)과 조회(읽기)를 분리하여 각 기능을 독립적으로 확장하고 최적화하는 패턴.

- **Eventual Consistency**  
  비동기 처리를 통해 시간이 지나면서 데이터 일관성을 달성하는 모델.

구성 요소
---------
초기 설계 단계에서는 다음과 같은 구성 요소를 고려합니다.

- **Command Bus**  
  클라이언트로부터 전달된 명령을 적절한 핸들러로 전달합니다.

- **Event Bus**  
  도메인 이벤트를 여러 컴포넌트에 전달하여 후속 처리를 유도합니다.

- **Event Store**  
  모든 이벤트를 기록하여 감사와 시스템 복구에 활용합니다.

- *(추후)* **Saga**  
  분산 트랜잭션을 관리하는 보상 메커니즘 (현재는 검토 단계)

워크플로우
-----------
예시로, 요구사항 생성 프로세스의 기본 흐름은 다음과 같습니다.

1. 사용자가 요구사항 생성 커맨드를 전송합니다.
2. 커맨드가 처리되어 도메인 이벤트(예: RequirementCreatedEvent)가 발행됩니다.
3. 이벤트를 구독하는 서비스에서 조회 모델 업데이트, 알림 전송 등 후속 작업을 수행합니다.

참고 자료
----------
- `마틴 파울러 이벤트 소싱 <https://martinfowler.com/eaaDev/EventSourcing.html>`_
- `Microsoft EDA 가이드 <https://docs.microsoft.com/ko-kr/azure/architecture/guide/architecture-styles/event-driven>`_

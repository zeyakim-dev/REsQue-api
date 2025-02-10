==========
테스트
==========

.. toctree::
   :maxdepth: 2
   :caption: 도메인 테스트

   unit/domain/user/test_cases
   
.. toctree::
   :maxdepth: 2
   :caption: 애플리케이션 테스트

   unit/application/auth/test_authenticate

.. toctree::
   :maxdepth: 2
   :caption: 인프라스트럭처 테스트

   unit/infrastructure/security/test_password_hasher

개요
----

테스트 구조
^^^^^^^^^^
* 도메인 테스트: 핵심 비즈니스 규칙 검증
* 애플리케이션 테스트: 유스케이스 시나리오 검증
* 인프라스트럭처 테스트: 기술적 구현 검증

테스트 원칙
^^^^^^^^^^
* 계층별 책임 분리
* 테스트 격리와 독립성
* 가독성과 유지보수성

테스트 문서화
^^^^^^^^^^^
* 시나리오 중심 기술
* 검증 항목 명확화
* 설계 원칙 명시 
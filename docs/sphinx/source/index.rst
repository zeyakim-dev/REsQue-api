.. REsQue-api 문서의 마스터 파일입니다. 
   sphinx-quickstart를 사용하여 2025년 1월 31일에 생성되었습니다.
   이 파일은 필요에 따라 자유롭게 수정할 수 있으며, 최소한 `toctree` 지시어를 포함해야 합니다.

REsQue-api 문서
========================

``reStructuredText`` 문법을 사용하여 내용을 추가하세요. 자세한 내용은
`reStructuredText 공식 문서 <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
를 참고하세요.

.. toctree::
   :maxdepth: 3
   :caption: 문서 목차

   design/index

==============
REsQue API 개요
===============

이 문서는 REsQue API의 설계 원칙과 테스트 전략을 설명합니다. REsQue API는 도메인 모델링, 이벤트 기반 아키텍처, 보안 정책을 중심으로 설계되었으며, 이를 검증하기 위한 다양한 테스트 전략을 포함하고 있습니다.

설계 문서
------------

REsQue API의 설계 원칙과 핵심 개념을 다루는 문서입니다.

- **도메인 설계**: 비즈니스 로직과 핵심 개념 정의
- **테스트 설계**: 효과적인 테스트 전략 및 실행 방안
- **보안 정책**: 비밀번호 정책 및 보안 강화 방안
- **이벤트 기반 아키텍처**: Event-Driven 구조 및 핵심 구성 요소

.. toctree::
   :maxdepth: 1
   :caption: 설계 문서

   design/domain/user/password_policy
   design/event_driven_architecture/index

테스트 문서
-----------

REsQue API의 기능을 검증하고 품질을 보장하는 테스트 문서입니다.

- **단위 테스트**: 개별 모듈 및 함수 테스트
- **통합 테스트**: 시스템 간 상호작용 검증
- **성능 테스트**: 응답 시간 및 부하 테스트

.. toctree::
   :maxdepth: 2
   :caption: 테스트 문서

   test/index
   

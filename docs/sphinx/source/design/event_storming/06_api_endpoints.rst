=================
API 엔드포인트
=================

인증 API
-----------------

회원가입
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/auth/register
    Content-Type: application/json

    Request:
    {
        "email": string,
        "password": string
    }

    Response: 201 Created
    {
        "id": UUID,
        "email": string
    }

로그인
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/auth/login
    Content-Type: application/json

    Request:
    {
        "email": string,
        "password": string
    }

    Response: 200 OK
    {
        "access_token": string
    }

Google OAuth
^^^^^^^^^^^^^^^^^
.. code-block:: text

    GET /api/auth/google/login
    GET /api/auth/google/callback

프로젝트 API
-----------------

프로젝트 생성
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/projects
    Content-Type: application/json
    Authorization: Bearer {token}

    Request:
    {
        "title": string,
        "description": string
    }

    Response: 201 Created
    {
        "id": UUID,
        "title": string,
        "description": string,
        "created_at": datetime
    }

프로젝트 조회
^^^^^^^^^^^^^^^^^
.. code-block:: text

    GET /api/projects/{project_id}
    Authorization: Bearer {token}

    Response: 200 OK
    {
        "id": UUID,
        "title": string,
        "description": string,
        "status": string,
        "members": [
            {
                "user_id": UUID,
                "email": string,
                "role": string
            }
        ]
    }

내 프로젝트 목록
^^^^^^^^^^^^^^^^^
.. code-block:: text

    GET /api/projects
    Authorization: Bearer {token}

    Response: 200 OK
    {
        "projects": [
            {
                "id": UUID,
                "title": string,
                "description": string,
                "status": string
            }
        ]
    }

초대 관리
-----------------

멤버 초대
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/projects/{project_id}/invitations
    Content-Type: application/json
    Authorization: Bearer {token}

    Request:
    {
        "email": string,
        "role": "VIEWER" | "MEMBER" | "MANAGER"
    }

    Response: 201 Created
    {
        "id": UUID,
        "email": string,
        "role": string,
        "expires_at": datetime
    }

초대 수락
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/invitations/{invitation_id}/accept
    Authorization: Bearer {token}

    Response: 200 OK
    {
        "project_id": UUID,
        "role": string
    }

초대 조회
^^^^^^^^^^^^^^^^^
.. code-block:: text

    GET /api/invitations/pending
    Authorization: Bearer {token}

    Response: 200 OK
    {
        "invitations": [
            {
                "id": UUID,
                "project_id": UUID,
                "project_title": string,
                "role": string,
                "expires_at": datetime
            }
        ]
    }

요구사항 API
-----------------

요구사항 생성
^^^^^^^^^^^^^^^^^
.. code-block:: text

    POST /api/projects/{project_id}/requirements
    Content-Type: application/json
    Authorization: Bearer {token}

    Request:
    {
        "title": string,
        "description": string
    }

    Response: 201 Created
    {
        "id": UUID,
        "title": string,
        "description": string,
        "status": "TODO"
    }

요구사항 상태 변경
^^^^^^^^^^^^^^^^^
.. code-block:: text

    PATCH /api/requirements/{requirement_id}
    Content-Type: application/json
    Authorization: Bearer {token}

    Request:
    {
        "status": "TODO" | "IN_PROGRESS" | "DONE"
    }

    Response: 200 OK
    {
        "id": UUID,
        "status": string,
        "updated_at": datetime
    }

프로젝트 요구사항 목록
^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

    GET /api/projects/{project_id}/requirements
    Authorization: Bearer {token}

    Response: 200 OK
    {
        "requirements": [
            {
                "id": UUID,
                "title": string,
                "description": string,
                "status": string,
                "assignee": {
                    "id": UUID,
                    "email": string
                }
            }
        ]
    }

공통 사항
-----------------

에러 응답
^^^^^^^^^^^^^^^^^
.. code-block:: text

    Response: 4XX/5XX
    {
        "error": {
            "code": string,
            "message": string
        }
    }

주요 에러 코드
^^^^^^^^^^^^^^^^^
- AUTH001: 인증 실패
- AUTH002: 유효하지 않은 토큰
- USER001: 존재하지 않는 사용자
- USER002: 이미 존재하는 이메일
- PRJ001: 존재하지 않는 프로젝트
- PRJ002: 프로젝트 접근 권한 없음
- INV001: 존재하지 않는 초대
- INV002: 만료된 초대
- REQ001: 존재하지 않는 요구사항 
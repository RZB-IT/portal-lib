import pytest

from rzbportal import Security, SecurityProvider

from fastapi import Request
import jwt

from rzbportal import UserData

JWT_SECRET = "abc"

MOCK_DATA = {
  "id_token": "b9da1d1b-9f22-4c0a-a8f6-c75e471c380d",
  "public_name": "Dummy public name",
  "member_number": 123,
  "id_user": "123e4567-e89b-12d3-a456-426614174000",
  "exp": 1734911490,
  "iat": 1734738690
}


# @pytest.fixture
# def mock_request() -> Request:
#     return Request(scope={
#         "type": "http",
#         "headers": {
#             ("Authorization".encode(), f"Bearer {jwt.encode(MOCK_DATA, JWT_SECRET, algorithm="HS256")}".encode()),
#         },
#     })

# @pytest.mark.unit
# @pytest.mark.asyncio()
# async def test_security(mock_request: Request):
#     provider = SecurityProvider(JWT_SECRET)
#     await provider(mock_request)

@pytest.mark.unit
@pytest.mark.asyncio()
async def test_security_acl():
    security = Security(
        user_data=UserData(
            id_token="b9da1d1b-9f22-4c0a-a8f6-c75e471c380d",
            public_name="Dummy public name",
            member_number=123,
            id_user="a39d10d3-3042-493f-a744-573abdd3fd78",
            exp=1734911490,
            iat=1734738690,
            acl=["LOGIN", "READ_SOME", "READ_OTHER"],
            email="test@test.cz"
        ),
        raw_jwt=jwt.encode(MOCK_DATA, JWT_SECRET, algorithm="HS256"),
        id_token="b9da1d1b-9f22-4c0a-a8f6-c75e471c380d"
    )

    assert security.can("LOGIN")
    assert security.can("READ_SOME")
    assert security.can("READ_OTHER")

    assert security.can_all(["LOGIN", "READ_SOME", "READ_OTHER"])
    assert security.can_all(["LOGIN", "READ_SOME"])
    assert security.can_all(["LOGIN", "READ_OTHER"])
    assert security.can_all(["READ_SOME", "READ_OTHER"])
    assert security.can_all(["LOGIN"])

    assert security.can_any(["LOGIN", "READ_SOME", "READ_OTHER"])
    assert security.can_any(["LOGIN", "READ_SOME"])
    assert security.can_any(["LOGIN", "READ_OTHER"])
    assert security.can_any(["READ_SOME", "READ_OTHER"])
    assert security.can_any(["LOGIN"])

    assert not security.can("WRITE")
    assert not security.can("DELETE")
    assert not security.can("UPDATE")

    assert not security.can_all(["LOGIN", "READ_SOME", "WRITE"])
    assert not security.can_all(["LOGIN", "READ_SOME", "DELETE"])
    assert not security.can_all(["LOGIN", "READ_SOME", "UPDATE"])
    assert not security.can_all(["LOGIN", "READ_OTHER", "WRITE"])
    assert not security.can_all(["LOGIN", "READ_OTHER", "DELETE"])
    assert not security.can_all(["LOGIN", "READ_OTHER", "UPDATE"])
    assert not security.can_all(["LOGIN", "WRITE", "DELETE"])
    assert not security.can_all(["LOGIN", "WRITE", "UPDATE"])
    assert not security.can_all(["LOGIN", "DELETE", "UPDATE"])
    assert not security.can_all(["READ_SOME", "WRITE", "DELETE"])
    assert not security.can_all(["READ_SOME", "WRITE", "UPDATE"])
    assert not security.can_all(["READ_SOME", "DELETE", "UPDATE"])
    assert not security.can_all(["READ_OTHER", "WRITE", "DELETE"])
    assert not security.can_all(["READ_OTHER", "WRITE", "UPDATE"])
    assert not security.can_all(["READ_OTHER", "DELETE", "UPDATE"])
    
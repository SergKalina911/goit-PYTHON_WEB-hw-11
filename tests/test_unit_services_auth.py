""" Юніт-тести для src.services.auth"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.services.auth import auth_service
from jose import jwt

SECRET = auth_service.SECRET_KEY
ALGO = auth_service.ALGORITHM

class DummyUser:
    def __init__(self, email):
        self.email = email

class DummyDB:
    async def get_user_by_email(self, email, db):
        return DummyUser(email)

@pytest.mark.asyncio
async def test_password_hash_and_verify():
    pwd = "secret123"
    hashed = auth_service.get_password_hash(pwd)
    assert auth_service.verify_password(pwd, hashed)
    assert not auth_service.verify_password("wrong", hashed)

@pytest.mark.asyncio
async def test_access_and_refresh_tokens():
    data = {"sub": "test@example.com"}
    access = await auth_service.create_access_token(data)
    refresh = await auth_service.create_refresh_token(data)

    # decode refresh
    decoded = await auth_service.decode_refresh_token(refresh)
    assert decoded == "test@example.com"

    # invalid scope
    bad_token = jwt.encode({"sub":"x","scope":"wrong"}, SECRET, algorithm=ALGO)
    with pytest.raises(HTTPException):
        await auth_service.decode_refresh_token(bad_token)

def test_email_token_encode_decode():
    token = auth_service.create_email_token({"sub":"mail@example.com"})
    decoded = auth_service.decode_email_token(token)
    assert decoded == "mail@example.com"

    # bad token
    assert auth_service.decode_email_token("bad.token") is None

def test_reset_token_encode_decode():
    token = auth_service.create_reset_token("reset@example.com")
    decoded = auth_service.decode_reset_token(token)
    assert decoded == "reset@example.com"

    # wrong scope
    bad_token = jwt.encode({"sub":"x","scope":"wrong"}, SECRET, algorithm=ALGO)
    assert auth_service.decode_reset_token(bad_token) is None

@pytest.mark.asyncio
async def test_get_current_user_valid(monkeypatch):
    data = {"sub":"user@example.com","scope":"access_token"}
    token = jwt.encode(data, SECRET, algorithm=ALGO)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    async def fake_get_user_by_email(email, db):
        return DummyUser(email)

    monkeypatch.setattr("src.repository.users.get_user_by_email", fake_get_user_by_email)

    user = await auth_service.get_current_user(credentials=creds, db=None)
    assert user.email == "user@example.com"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token")
    with pytest.raises(HTTPException):
        await auth_service.get_current_user(credentials=creds, db=None)

def test_decode_reset_token_invalid_scope():
    bad_token = jwt.encode({"sub":"x","scope":"wrong"}, SECRET, algorithm=ALGO)
    assert auth_service.decode_reset_token(bad_token) is None

def test_decode_reset_token_invalid_token():
    assert auth_service.decode_reset_token("bad.token") is None

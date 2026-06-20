""" Юніт-тести для src.routes.users.upload_avatar """

import pytest
from fastapi import UploadFile, HTTPException
from io import BytesIO

from src.routes import users

class DummyDB:
    def __init__(self):
        self.committed = False
        self.refreshed = False
    def commit(self): self.committed = True
    def refresh(self, obj): self.refreshed = True

class DummyUser:
    def __init__(self):
        self.avatar = None

@pytest.mark.asyncio
async def test_upload_avatar_success(monkeypatch):
    # замокаємо cloudinary.uploader.upload
    def fake_upload(file, folder):
        return {"secure_url": "http://fake.cloudinary/avatar.png"}
    monkeypatch.setattr(users.cloudinary.uploader, "upload", fake_upload)

    db = DummyDB()
    user = DummyUser()
    file = UploadFile(file=BytesIO(b"fake image"), filename="avatar.png")

    result = await users.upload_avatar(file=file, db=db, user=user)
    assert result["avatar_url"] == "http://fake.cloudinary/avatar.png"
    assert user.avatar == "http://fake.cloudinary/avatar.png"
    assert db.committed and db.refreshed

@pytest.mark.asyncio
async def test_upload_avatar_failure(monkeypatch):
    def fake_upload(file, folder):
        raise Exception("Cloudinary error")
    monkeypatch.setattr(users.cloudinary.uploader, "upload", fake_upload)

    db = DummyDB()
    user = DummyUser()
    file = UploadFile(file=BytesIO(b"fake image"), filename="avatar.png")

    with pytest.raises(HTTPException) as exc:
        await users.upload_avatar(file=file, db=db, user=user)
    assert exc.value.status_code == 500
    assert "Cloudinary error" in exc.value.detail

from pydantic import BaseModel, EmailStr
from datetime import date
from datetime import datetime

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra_info: str | None = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str | None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

""" Код зі схемами Pydantic для валідації даних та опису моделей, які використовуються у додатку"""
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class ContactBase(BaseModel):
    """ Базова схема для контактів, яка містить загальні поля, такі як ім'я, прізвище, email,
    телефон, дата народження та додаткова інформація. Ця схема використовується як основа для
    створення та оновлення контактів. Вона забезпечує валідацію даних та визначає типи полів,
    що допомагає уникнути помилок при обробці даних користувача.   """
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
    confirmed: bool
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class RequestEmail(BaseModel):
    email: EmailStr

# ✅ нові схеми для reset password
class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    new_password: str

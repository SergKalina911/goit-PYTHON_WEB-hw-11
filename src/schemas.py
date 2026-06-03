""" Код зі схемами Pydantic для валідації даних та опису моделей, які використовуються у  додатку. """
from pydantic import BaseModel, EmailStr
from datetime import date
from datetime import datetime

class ContactBase(BaseModel):
    """ Базова модель для контактів, яка містить спільні поля для створення та оновлення контактів. """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra_info: str | None = None

class ContactCreate(ContactBase):
    """ Модель для створення нового контакту. """
    pass

class ContactUpdate(ContactBase):
    """ Модель для оновлення існуючого контакту. """
    pass

class Contact(ContactBase):
    """ Модель для представлення контакту з додатковим полем id. """
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserModel(BaseModel):
    """ Модель для створення нового користувача. """
    username: str
    email: EmailStr
    password: str

class UserDb(BaseModel):
    """ Модель для представлення користувача з додатковими полями. """

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str | None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """ Модель для представлення відповіді при створенні користувача. """
    user: UserDb
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    """ Модель для представлення токенів доступу та оновлення. """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    """ Модель для представлення даних при логіні користувача. """
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    """ Модель для представлення даних при оновленні токенів. """
    refresh_token: str
    
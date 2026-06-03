""" Сервіс для аутентифікації користувачів. """
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users

class Auth:
    """ Сервіс для аутентифікації користувачів. Включає методи для перевірки паролів, генерації та
    декодування JWT токенів, а також отримання поточного користувача на основі токена. Використовує
    bcrypt для безпечного хешування паролів та jose для роботи з JWT. """

    # Контекст для роботи з паролями
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Налаштування для JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    # ✅ Тепер використовуємо HTTPBearer, а не OAuth2PasswordBearer
    oauth2_scheme = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ Перевіряє, чи відповідає простий пароль захешованому. Використовує bcrypt для
        безпечного порівняння. """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """ Генерує хеш пароля. """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """ Створює JWT токен для аутентифікації користувача. Включає в payload дані користувача,
        час закінчення дії токена та тип токена (access_token). Термін дії токена визначається
        через змінну оточення або за замовчуванням 15 хвилин. """
        expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        to_encode = {**data, "exp": expire, "scope": "access_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """ Створює JWT токен для оновлення доступу користувача. Включає в payload дані
        користувача, час закінчення дії токена та тип токена (refresh_token). Термін дії токена
        визначається через змінну оточення або за замовчуванням 7 днів. """
        expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        expire = datetime.utcnow() + timedelta(days=expire_days)
        to_encode = {**data, "exp": expire, "scope": "refresh_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """ Декодує JWT токен оновлення. Перевіряє валідність токена, його тип та повертає
        email користувача. Якщо токен недійсний або має неправильний тип, повертає помилку 401. """
        payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid scope")
        return payload["sub"]

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """ Отримує поточного користувача на основі JWT токена. Перевіряє валідність токена, його
        тип та наявність користувача в базі даних.Якщо токен недійсний або користувач не знайдений,
        повертає помилку 401."""
        try:
            # ⚠️ Тепер беремо чистий токен без "Bearer"
            payload = jwt.decode(credentials.credentials, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        if payload.get("scope") != "access_token":
            raise HTTPException(status_code=401, detail="Invalid scope")

        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = await repository_users.get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    
# ✅ Єдиний екземпляр класу
auth_service = Auth()

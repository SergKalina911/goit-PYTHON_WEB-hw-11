""" Сервіс для аутентифікації користувачів. """
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users

class Auth:
    """ Клас для аутентифікації користувачів. Тут ми реалізуємо функції для хешування паролів,
    створення та декодування JWT-токенів, а також отримання поточного користувача на основі
    токена. Ми використовуємо бібліотеку passlib для безпечного хешування паролів та jose для
    роботи з JWT. Клас також містить методи для створення токенів підтвердження email та
    скидання пароля.  Цей сервіс є ключовим компонентом для забезпечення безпеки та управління
    доступом у нашому додатку.  """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    oauth2_scheme = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ 
        Перевірка відповідності введеного пароля та захешованого пароля в базі даних.
        
        :param plain_password: Введений користувачем пароль.
        :type plain_password: str
        :param hashed_password: Захешований пароль, збережений у базі даних.
        :type hashed_password: str
        :return: True, якщо паролі співпадають, інакше False.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """ 
        Хешування пароля перед збереженням у базі даних. 
        :param password: Пароль, який потрібно захешувати.
        :type password: str
        :return: Захешований пароль.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """ 
        Створення JWT-токена для аутентифікації користувача. Токен містить інформацію про
        користувача та час його дії.
        
        :param data: Дані для кодування в токен.
        :type data: dict
        :param expires_delta: Час дії токена в хвилинах.
        :type expires_delta: Optional[int]
        :return: JWT-токен.
        :rtype: str
        """
        expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        to_encode = {**data, "exp": expire, "scope": "access_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """ 
        Створення JWT-токена для оновлення access token. Цей токен має більший час дії та
        використовується для отримання нового access token без повторної аутентифікації
        користувача.
        
        :param data: Дані для кодування в токен.
        :type data: dict
        :param expires_delta: Час дії токена в днях.
        :type expires_delta: Optional[int]
        :return: JWT-токен.
        :rtype: str
        """
        expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        expire = datetime.utcnow() + timedelta(days=expire_days)
        to_encode = {**data, "exp": expire, "scope": "refresh_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """ 
        Декодування refresh token для отримання інформації про користувача. Цей метод перевіряє
        валідність токена та його тип (scope), щоб переконатися, що це саме refresh token. Якщо
        токен недійсний або має неправильний scope, буде піднято HTTPException.
        
        :param refresh_token: JWT-токен для оновлення access token.
        :type refresh_token: str
        :return: ID користувача.
        :rtype: str
        """
        payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid scope")
        return payload["sub"]

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> repository_users.User:
        """ 
        Отримання поточного користувача на основі JWT-токена, переданого в заголовку
        Authorization. Цей метод декодує токен, перевіряє його валідність та отримує
        інформацію про користувача з бази даних. Якщо токен недійсний або користувач не
        знайдений, буде піднято HTTPException.
        
        :param credentials: Об'єкт, що містить JWT-токен з заголовка Authorization.
        :type credentials: HTTPAuthorizationCredentials
        :param db: Сесія бази даних.
        :type db: Session
        :return: Поточний користувач.
        :rtype: repository_users.User
        """
        try:
            payload = jwt.decode(credentials.credentials, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
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
    
    def create_email_token(self, data: dict) -> str:
        """
        Створення JWT-токена для підтвердження email. Цей токен містить інформацію про
        користувача та час його дії. Використовується для підтвердження email-адреси користувача
        після реєстрації.
        
        :param data: Дані для кодування в токен (зазвичай містить email користувача).
        :type data: dict
        :return: JWT-токен для підтвердження email.
        :rtype: str
        """
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {**data, "iat": datetime.utcnow(), "exp": expire}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_email_token(self, token: str) -> str | None:
        """
        Декодування JWT-токена для підтвердження email. Цей метод перевіряє валідність токена та
        отримує інформацію про користувача. Якщо токен недійсний або має неправильний формат, буде
        повернуто None.
        
        :param token: JWT-токен для підтвердження email.
        :type token: str
        :return: Email користувача або None.
        :rtype: str or None
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None

    # ✅ нові методи для reset password
    def create_reset_token(self, email: str) -> str:
        """
        Створення JWT-токена для скидання пароля. Цей токен містить email користувача та час
        його дії. Використовується для відправки посилання на скидання пароля користувачу.
                
        :param email: Email користувача, для якого створюється токен.
        :type email: str
        :return: JWT-токен для скидання пароля.
        :rtype: str
        """
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode = {"sub": email, "exp": expire, "scope": "reset_password"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_reset_token(self, token: str) -> Optional[str] | None:
        """
        Декодування JWT-токена для скидання пароля. Цей метод перевіряє валідність токена
        та його тип (scope), щоб переконатися, що це саме reset password token. Якщо токен
        недійсний або має неправильний scope, буде повернуто None. Якщо токен валідний, буде
        повернуто email користувача.
        
        :param token: JWT-токен для скидання пароля.
        :type token: str
        :return: Email користувача або None.
        :rtype: str or None
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "reset_password":
                return None
            return payload.get("sub")
        except JWTError:
            return None

auth_service = Auth()

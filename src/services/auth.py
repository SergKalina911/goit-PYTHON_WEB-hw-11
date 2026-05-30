from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.database import models
from src.database.db import get_db
from src.repository import users as repository_users
from src import schemas
from typing import Optional


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode = {**data, "exp": expire, "scope": "access_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {**data, "exp": expire, "scope": "refresh_token"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def decode_refresh_token(self, refresh_token: str):
        payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload['scope'] != 'refresh_token':
            raise HTTPException(status_code=401, detail="Invalid scope")
        return payload['sub']

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload['scope'] != 'access_token':
            raise HTTPException(status_code=401, detail="Invalid scope")
        email = payload['sub']
        user = await repository_users.get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

auth_service = Auth()

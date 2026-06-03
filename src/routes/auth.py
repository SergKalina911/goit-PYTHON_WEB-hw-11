""" Контролер для аутентифікації користувачів: реєстрація, логін та оновлення токенів. """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, UserLogin, RefreshRequest
from src.repository import users as repository_users
from src.services.auth import auth_service  # ✅ екземпляр класу Auth

router = APIRouter(prefix="/auth", tags=["auth"])

# 🟢 Реєстрація
@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(status_code=409, detail="Email already registered")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}

# 🟢 Логін через JSON тіло
@router.post("/login", response_model=TokenModel)
async def login(body: UserLogin, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None or not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# 🟢 Оновлення токенів через refresh
@router.post("/refresh", response_model=TokenModel)
async def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    token = body.refresh_token
    if not token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None or user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

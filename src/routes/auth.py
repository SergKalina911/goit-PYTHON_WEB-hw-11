""" Маршрути для аутентифікації та авторизації користувачів.
Реєстрація, логін, оновлення токенів, підтвердження email, скидання паролю.
- Реєстрація: створення нового користувача, хешування паролю, відправка листа з підтвердженням.
- Логін: перевірка облікових даних, генерація JWT токенів, кешування користувача у Redis.
- Оновлення токенів: генерація нових токенів при запиті, оновлення кешу.
- Підтвердження email: обробка посилання з токеном, активація облікового запису.
- Скидання паролю: запит на скидання, відправка листа з посиланням, обробка нового паролю.
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import (
    UserModel, UserResponse, TokenModel, UserLogin,
    ResetPasswordRequest, ResetPasswordConfirm
)
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_verification_email, send_reset_password_email
from src.services.cache import cache_user, get_cached_user   # ✅ кеш

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """ Реєстрація нового користувача """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    token = auth_service.create_email_token({"sub": new_user.email})
    background_tasks.add_task(send_verification_email, new_user.email, new_user.username, str(request.base_url), token)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """ Підтвердження користувача через email """
    email = auth_service.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user.confirmed = True
    db.commit()
    return {"message": "Email confirmed successfully"}

@router.post("/login", response_model=TokenModel)
async def login(body: UserLogin, db: Session = Depends(get_db)):
    """ Логін користувача """

    # ✅ спочатку пробуємо взяти користувача з кешу по id
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        cached_user = get_cached_user(user.id)
        if cached_user and auth_service.verify_password(body.password, user.password):
            print(f"⚡ Використано кеш для {body.email}")  # 🔎 тестовий print
            return {
                "access_token": cached_user["access_token"],
                "refresh_token": cached_user["refresh_token"],
                "token_type": "bearer"
            }

    # якщо немає в кеші — перевіряємо користувача у БД
    if user is None or not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    access_token = await auth_service.create_access_token({"sub": user.email})
    refresh_token = await auth_service.create_refresh_token({"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    
    # ✅ кешуємо користувача після успішного логіну (передаємо об’єкт user)
    cache_user(user, access_token, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(user=Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """ Оновлення токенів для авторизованого користувача """
    access_token = await auth_service.create_access_token({"sub": user.email})
    refresh_token = await auth_service.create_refresh_token({"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    # ✅ оновлюємо кеш (передаємо об’єкт user)
    cache_user(user, access_token, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/reset-password-request")
async def reset_password_request(body: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """ Запит на скидання паролю """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = auth_service.create_reset_token(user.email)
    await send_reset_password_email(user.email, str(request.base_url), token)
    return {"message": "Password reset email sent"}

@router.post("/reset-password/{token}")
async def reset_password(token: str, body: ResetPasswordConfirm, db: Session = Depends(get_db)):
    """ Скидання паролю за токеном, отриманим з email """
    email = auth_service.decode_reset_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.password = auth_service.get_password_hash(body.new_password)
    db.commit()
    return {"message": "Password reset successful"}

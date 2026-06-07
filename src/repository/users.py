""" Створення користувача та отримання даних про нього. """
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
# from src.database import models


async def get_user_by_email(email: str, db: Session) -> User:
    """ Отримання користувача за його email. """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """ Створення нового користувача. """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    """ Оновлення токена користувача. """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """ Підтвердження email користувача. """
    user = await get_user_by_email(email, db)
    if user:   # ✅ перевірка
        user.confirmed = True
        db.commit()
    

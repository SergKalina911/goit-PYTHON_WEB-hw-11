""" Створення користувача та отримання даних про нього. """
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel

async def get_user_by_email(email: str, db: Session) -> User:
    """ Отримання користувача за його email.
    
    :param email: Email користувача
    :type email: str
    :param db: Сесія бази даних
    :type db: Session
    :return: Користувач або None
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """ Створення нового користувача.
    
    :param body: Дані для створення користувача
    :type body: UserModel
    :param db: Сесія бази даних
    :type db: Session
    :return: Створений користувач
    :rtype: User
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    """ Оновлення токена користувача.
    
    :param user: Користувач
    :type user: User
    :param token: Новий токен
    :type token: str | None
    :param db: Сесія бази даних
    :type db: Session
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """ Підтвердження email користувача.
    
    :param email: Email користувача
    :type email: str
    :param db: Сесія бази даних
    :type db: Session
    """
    user = await get_user_by_email(email, db)
    if user:   # ✅ перевірка
        user.confirmed = True
        db.commit()
    

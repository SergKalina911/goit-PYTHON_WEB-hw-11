""" Модуль для роботи з контактами у базі даних. Тут ми визначаємо функції для отримання, створення
оновлення та видалення контактів. Кожна функція приймає сесію бази даних та поточного користувача,
щоб забезпечити,що користувач може працювати лише зі своїми контактами. Ми також реалізуємо функцію
для пошуку контактів за певним запитом та функцію для отримання контактів з майбутніми днями
народженнями. """
from sqlalchemy.orm import Session
from datetime import date, timedelta
from src.database import models
from src import schemas

async def get_contacts(db: Session, user: models.User) -> list[models.Contact]:
    """
    Отримати всі контакти поточного користувача.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Список контактів користувача
    :rtype: list[:class:`src.database.models.Contact`]
    
    """
    return db.query(models.Contact).filter(models.Contact.user_id == user.id).all()

async def get_contact(db: Session, contact_id: int, user: models.User) -> models.Contact | None:
    """
    Отримати контакт за ID, якщо він належить поточному користувачу.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param contact_id: ID контакту
    :type contact_id: int
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Контакт або None
    :rtype: src.database.models.Contact | None
    
    """
    # шукаємо контакт за ID, але тільки серед контактів користувача
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.user_id == user.id
    ).first()

async def create_contact(db: Session, contact: schemas.ContactCreate, user: models.User) -> models.Contact:
    """
    Створити новий контакт для поточного користувача.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param contact: Дані для створення контакту
    :type contact: schemas.ContactCreate
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Створений контакт
    :rtype: src.database.models.Contact
    
    """
    # створюємо контакт і додаємо user_id
    db_contact = models.Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

async def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user: models.User) -> models.Contact | None:
    """
    Оновити існуючий контакт для поточного користувача.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param contact_id: ID контакту
    :type contact_id: int
    
    :param contact: Дані для оновлення контакту
    :type contact: schemas.ContactUpdate
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Оновлений контакт або None
    :rtype: src.database.models.Contact | None
    
    """
    db_contact = await get_contact(db, contact_id, user)
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

async def delete_contact(db: Session, contact_id: int, user: models.User) -> models.Contact | None:
    """
    Видалити контакт для поточного користувача.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param contact_id: ID контакту
    :type contact_id: int
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Видалений контакт або None
    :rtype: src.database.models.Contact | None
    
    """
    db_contact = await get_contact(db, contact_id, user)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

async def search_contacts(db: Session, query: str, user: models.User) -> list[models.Contact]:
    """
    Пошук контактів за певним запитом для поточного користувача.
    
    :param db: Сесія бази даних
    :type db: Session
    
    :param query: Запит для пошуку
    :type query: str
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Список знайдених контактів
    :rtype: list[:class:`src.database.models.Contact`]
    
    """
    # пошук лише серед контактів користувача
    return db.query(models.Contact).filter(
        models.Contact.user_id == user.id,
        (
            models.Contact.first_name.ilike(f"%{query}%") |
            models.Contact.last_name.ilike(f"%{query}%") |
            models.Contact.email.ilike(f"%{query}%")
        )
    ).all()

async def upcoming_birthdays(db: Session, user: models.User) -> list[models.Contact]:
    """
    Отримати контакти з майбутніми днями народженнями для поточного користувача.

    :param db: Сесія бази даних
    :type db: Session
    
    :param user: Поточний користувач
    :type user: models.User
    
    :return: Список контактів з майбутніми днями народженнями
    :rtype: list[:class:`src.database.models.Contact`]
    
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(models.Contact).filter(models.Contact.user_id == user.id).all()
    result = []

    for contact in contacts:
        if contact.birthday:
            try:
                # Беремо лише день і місяць, рік замінюємо на поточний
                birthday_this_year = contact.birthday.replace(year=today.year)
            except ValueError:
                # Якщо день народження 29 лютого, а рік не високосний — пропускаємо
                continue

            if today <= birthday_this_year <= next_week:
                result.append(contact)

    return result

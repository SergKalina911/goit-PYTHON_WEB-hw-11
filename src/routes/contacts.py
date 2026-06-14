""" Маршрути для роботи з контактами.
CRUD-операції, пошук та отримання контактів з днями народження.
Доступні лише для авторизованих користувачів.
"""

from fastapi import APIRouter, Depends, status, HTTPException, Security
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, Contact
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter  # ✅ імпорт для rate limiting
from pyrate_limiter import Duration, Limiter, Rate  # ✅ імпорт для налаштування лімітерів


router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate,
                         db: Session = Depends(get_db),
                         user=Depends(auth_service.get_current_user),
                         _: None = Depends(RateLimiter(
                             limiter=Limiter(Rate(5, Duration.SECOND * 60)))
                         )) -> Contact:
    """ 
    Створити новий контакт. Накладається обмеження на кількість запитів: максимум 5
    запитів на хвилину. Лише авторизовані користувачі можуть створювати контакти.
    
    :param body: Дані для створення контакту.
    :type body: ContactCreate
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Створений контакт.
    :rtype: src.schemas.Contact
    
    """
    return await repository_contacts.create_contact(db, body, user)


@router.get("/", response_model=list[Contact])
async def get_contacts(db: Session = Depends(get_db),
                       user=Depends(auth_service.get_current_user)) -> list[Contact]:
    """
    Отримати всі контакти користувача. Лише авторизовані користувачі можуть
    отримувати свої контакти.
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Список контактів.
    :rtype: list[src.schemas.Contact]
    
    """
    return await repository_contacts.get_contacts(db, user)

@router.get("/search/", response_model=list[Contact])
async def search_contacts(query: str,
                          db: Session = Depends(get_db),
                          user=Depends(auth_service.get_current_user)) -> list[Contact]:
    """
    Пошук контактів за ім’ям, прізвищем або email. Лише авторизовані користувачі можуть
    виконувати пошук.
    
    :param query: Рядок для пошуку.
    :type query: str
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Список контактів.
    :rtype: list[src.schemas.Contact]
    
    """
    return await repository_contacts.search_contacts(db, query, user)

@router.get("/birthdays/", response_model=list[Contact])
async def upcoming_birthdays(db: Session = Depends(get_db),
                             user=Depends(auth_service.get_current_user)) -> list[Contact]:
    """
    Список контактів з днями народження у найближчі 7 днів. Лише авторизовані користувачі можуть
    отримувати цей список.
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Список контактів.
    :rtype: list[src.schemas.Contact]
    
    """
    return await repository_contacts.upcoming_birthdays(db, user)

# --- Динамічні маршрути ---
@router.get("/{contact_id}", response_model=Contact)
async def get_contact(contact_id: int,
                      db: Session = Depends(get_db),
                      user=Depends(auth_service.get_current_user)) -> Contact:
    """
    Отримати контакт за ID. Лише авторизовані користувачі можуть отримувати інформацію про свої
    контакти.

    :param contact_id: ID контакту.
    :type contact_id: int
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Контакт.
    :rtype: src.schemas.Contact
    
    """
    contact = await repository_contacts.get_contact(db, contact_id, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int,
                         body: ContactUpdate,
                         db: Session = Depends(get_db),
                         user=Depends(auth_service.get_current_user)) -> Contact:
    """
    Оновити контакт за ID. Лише авторизовані користувачі можуть оновлювати свої контакти.

    :param contact_id: ID контакту.
    :type contact_id: int
    
    :param body: Дані для оновлення контакту.
    :type body: ContactUpdate
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Оновлений контакт.
    :rtype: src.schemas.Contact
    
    """
    contact = await repository_contacts.update_contact(db, contact_id, body, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}")
async def delete_contact(contact_id: int,
                         db: Session = Depends(get_db),
                         user=Depends(auth_service.get_current_user)) -> dict:
    """
    Видалити контакт за ID. Лише авторизовані користувачі можуть видаляти свої контакти.

    :param contact_id: ID контакту.
    :type contact_id: int
    
    :param db: Сесія бази даних.
    :type db: Session
    
    :param user: Поточний авторизований користувач.
    :type user: User
    
    :return: Повідомлення про успішне видалення.
    :rtype: dict
    
    """
    contact = await repository_contacts.delete_contact(db, contact_id, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return {"message": "Contact deleted"}

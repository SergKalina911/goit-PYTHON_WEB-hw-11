""" Маршрути для роботи з контактами.
CRUD-операції, пошук та отримання контактів з днями народження.
Доступні лише для авторизованих користувачів.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, Contact
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter  # ✅ новий імпорт для rate limiting

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(5, 60))])  # ✅ обмеження: 5 створень за хвилину
async def create_contact(body: ContactCreate, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Створення нового контакту. """
    return await repository_contacts.create_contact(body, db, user)

@router.get("/", response_model=list[Contact])
async def get_contacts(db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Отримати всі контакти користувача. """
    return await repository_contacts.get_contacts(db, user)

@router.get("/{contact_id}", response_model=Contact)
async def get_contact(contact_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Отримати контакт за ID. """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Оновити контакт за ID. """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Видалити контакт за ID. """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return {"message": "Contact deleted"}

@router.get("/search/", response_model=list[Contact])
async def search_contacts(query: str, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Пошук контактів за ім’ям, прізвищем або email. """
    return await repository_contacts.search_contacts(query, db, user)

@router.get("/birthdays/", response_model=list[Contact])
async def upcoming_birthdays(db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """ Список контактів з днями народження у найближчі 7 днів. """
    return await repository_contacts.upcoming_birthdays(db, user)

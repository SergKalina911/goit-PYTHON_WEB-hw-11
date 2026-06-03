""" Схема маршрутів для роботи з контактами користувача. Включає створення, читання, оновлення та
видалення контактів, а також пошук та перегляд майбутніх днів народження.  """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.repository import contacts as repository
from src import schemas
from src.database.db import get_db
from src.services.auth import auth_service
from src.database import models

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=schemas.Contact, status_code=201)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Створює новий контакт для поточного користувача. Перевіряє, чи існує контакт з таким же
    ім'ям та прізвищем, щоб уникнути дублікатів. """
    return repository.create_contact(db, contact, current_user)

@router.get("/", response_model=list[schemas.Contact])
def read_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Отримує список контактів для поточного користувача. """
    return repository.get_contacts(db, current_user)

@router.get("/search/", response_model=list[schemas.Contact])
def search_contacts(
    query: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Пошук контактів за певним запитом для поточного користувача. """
    return repository.search_contacts(db, query, current_user)

@router.get("/birthdays/", response_model=list[schemas.Contact])
def upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Отримує список контактів з майбутніми днями народженнями для поточного користувача. """
    return repository.upcoming_birthdays(db, current_user)

@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Отримує контакт за його ID для поточного користувача. Якщо контакт не знайдено, повертає
    помилку 404. """
    contact = repository.get_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Оновлює контакт за його ID для поточного користувача. Якщо контакт не знайдено, повертає
    помилку 404. """
    updated = repository.update_contact(db, contact_id, contact, current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    """ Видаляє контакт за його ID для поточного користувача. Якщо контакт не знайдено, повертає
    помилку 404. """
    deleted = repository.delete_contact(db, contact_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted"}
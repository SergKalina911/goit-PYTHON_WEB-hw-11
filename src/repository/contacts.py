from sqlalchemy.orm import Session
from datetime import date, timedelta
from src.database import models
from src import schemas

def get_contacts(db: Session):
    return db.query(models.Contact).all()

def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, query: str):
    return db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%"))
    ).all()

def upcoming_birthdays(db: Session):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(models.Contact).all()
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

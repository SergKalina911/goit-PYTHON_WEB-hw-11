from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.repository import contacts as repository
from src import schemas
from src.database.db import get_db

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return repository.create_contact(db, contact)

@router.get("/", response_model=list[schemas.Contact])
def read_contacts(db: Session = Depends(get_db)):
    return repository.get_contacts(db)

@router.get("/search/")
def search_contacts(query: str, db: Session = Depends(get_db)):
    return repository.search_contacts(db, query)

@router.get("/birthdays/")
def upcoming_birthdays(db: Session = Depends(get_db)):
    return repository.upcoming_birthdays(db)


@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repository.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    updated = repository.update_contact(db, contact_id, contact)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete_contact(db, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted"}


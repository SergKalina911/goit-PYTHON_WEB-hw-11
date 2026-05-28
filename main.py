from fastapi import FastAPI
from src.routes import contacts
from src.database.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts REST API")

app.include_router(contacts.router)

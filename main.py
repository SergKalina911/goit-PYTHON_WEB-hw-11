from fastapi import FastAPI
from src.routes import contacts, auth
from src.database.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts REST API with Auth")

# 🔑 підключаємо роутери
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

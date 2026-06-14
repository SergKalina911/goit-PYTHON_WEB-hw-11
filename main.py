""" Головний файл для запуску FastAPI додатку. """

from fastapi import FastAPI
from src.routes import contacts, auth, users
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Contacts REST API with Auth",
    swagger_ui_parameters={"persistAuthorization": True}
)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можна обмежити конкретними доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 підключаємо роутери
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

""" Головний файл для запуску FastAPI додатку. Тут ми створюємо екземпляр FastAPI та підключаємо
роутери для контактів та аутентифікації.  """
from fastapi import FastAPI
from src.routes import contacts, auth

app = FastAPI(
    title="Contacts REST API with Auth",
    swagger_ui_parameters={"persistAuthorization": True}
)
# 🔑 підключаємо роутери
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

""" Головний файл для запуску FastAPI додатку. """

from fastapi import FastAPI
from src.routes import contacts, auth, users
from fastapi.middleware.cors import CORSMiddleware
# from fastapi_limiter.depends import RateLimiter

# import redis.asyncio as redis
# import os

app = FastAPI(
    title="Contacts REST API with Auth",
    swagger_ui_parameters={"persistAuthorization": True}
)

# # ✅ Ініціалізація FastAPILimiter
# @app.on_event("startup")
# async def startup():
#     """ Ініціалізація FastAPILimiter при запуску додатку. Підключаємось до Redis."""
#     redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
#     redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
#     await FastAPILimiter.init(redis_client)

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

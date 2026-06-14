""" Маршрут для роботи з користувачами, зокрема для завантаження аватарів на Cloudinary."""
import os
from fastapi import APIRouter, UploadFile, Depends, HTTPException
import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

@router.post("/avatar")
async def upload_avatar(file: UploadFile, db: Session = Depends(get_db),
                        user=Depends(auth_service.get_current_user)) -> dict:
    """
    Завантаження аватара користувача на Cloudinary та оновлення URL в базі даних.
    
    :param file: Файл аватара для завантаження.
    :type file: UploadFile
    :param db: Сесія бази даних.
    :type db: Session
    :param user: Поточний авторизований користувач.
    :type user: User
    :return: Словник з URL аватара.
    :rtype: dict
    """
    try:
        result = cloudinary.uploader.upload(file.file, folder="avatars")
        user.avatar = result["secure_url"]
        db.commit()
        db.refresh(user)
        return {"avatar_url": user.avatar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

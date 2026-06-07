""" Модуль для роботи з відправкою електронних листів користувачам. Цей модуль містить функції для
відправки листів з підтвердженням реєстрації та скидання пароля. Використовується бібліотека
FastAPI-Mail для інтеграції з різними поштовими сервісами. Конфігурація для підключення до
поштового сервера зберігається у змінних оточення, що дозволяє легко налаштовувати відправку листів
без необхідності змінювати код.  Функції send_verification_email та send_reset_password_email
відповідають за формування та відправку відповідних листів користувачам. Вони використовують
шаблони HTML для створення привабливого та інформативного вмісту листів. У разі виникнення
помилок при підключенні до поштового сервера, помилки будуть виведені у консоль для подальшого
аналізу.    """
import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_verification_email(email: EmailStr, username: str, host: str, token: str):
    """ Відправка листа з підтвердженням реєстрації. Ця функція формує лист з посиланням для
    підтвердження реєстрації, яке містить JWT-токен для підтвердження email-адреси користувача.
    Лист відправляється на вказану email-адресу користувача. У разі виникнення помилок при 
    підключенні до поштового сервера, помилки будуть виведені у консоль для подальшого аналізу."""
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

async def send_reset_password_email(email: EmailStr, host: str, token: str):
    """ Відправка листа для скидання пароля. Ця функція формує лист з посиланням для скидання
    пароля, яке містить JWT-токен для підтвердження права на скидання пароля. Лист відправляється
    на вказану email-адресу користувача. У разі виникнення помилок при підключенні до поштового
    сервера, помилки будуть виведені у консоль для подальшого аналізу.    """
    try:
        reset_link = f"{host}api/auth/reset-password/{token}"
        message = MessageSchema(
            subject="Відновлення паролю у Contacts API",
            recipients=[email],
            template_body={"reset_link": reset_link},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)

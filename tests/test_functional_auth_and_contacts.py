""" Функцінальні тести для аутентифікації та роботи з контактами. """

import pytest
from httpx import AsyncClient, ASGITransport
import httpx
import sys
import os
import uuid
import base64
import re


# додаємо корінь проєкту (/app) у sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

MAILHOG_API = "http://mailhog:8025/api/v2/messages"

def extract_token_from_mailhog(keyword: str) -> str:
    resp = httpx.get(MAILHOG_API)
    resp.raise_for_status()
    items = resp.json()["items"]
    assert items, "No emails captured in MailHog"

    # перевіряємо всі листи, від останнього до першого
    for item in items[::-1]:
        raw_body = item["Content"]["Body"]

        # шукаємо секцію base64
        lines = raw_body.splitlines()
        collecting = False
        base64_lines = []
        for line in lines:
            if "Content-Transfer-Encoding: base64" in line:
                collecting = True
                continue
            if collecting:
                if line.startswith("--"):  # кінець секції
                    break
                if not line.startswith("Content-"):
                    base64_lines.append(line.strip())

        if not base64_lines:
            continue

        decoded_html = base64.b64decode("".join(base64_lines)).decode("utf-8")
        print("DECODED HTML:\n", decoded_html)

        if keyword == "confirm":
            match = re.search(r"/api/auth/confirmed_email/([^\"]+)", decoded_html)
            if match:
                return match.group(1).strip()

        if keyword == "reset-password":
            match = re.search(r"/api/auth/reset-password/([^\"]+)", decoded_html)
            if match:
                return match.group(1).strip()

    raise AssertionError(f"{keyword} token not found in any email body")


@pytest.mark.asyncio
async def test_full_auth_and_contacts_flow(reset_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Signup (унікальні дані)
        unique_email = f"ivan_{uuid.uuid4().hex[:6]}@example.com"
        user_data = {
            "username": f"ivan_{uuid.uuid4().hex[:6]}",
            "email": unique_email,
            "password": "secret123"
        }
        signup = await ac.post("/api/auth/signup", json=user_data)
        assert signup.status_code == 201

        # 2. Confirm email (через MailHog)
        token = extract_token_from_mailhog("confirm")
        confirm = await ac.get(f"/api/auth/confirmed_email/{token}")
        assert confirm.status_code == 200

        # 3. Login (два поля)
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login = await ac.post("/api/auth/login", json=login_data)
        assert login.status_code == 200
        tokens = login.json()
        access = tokens["access_token"]
        refresh = tokens["refresh_token"]

        headers = {"Authorization": f"Bearer {access}"}

        # 4. Authorization check
        check = await ac.get("/api/auth/check", headers=headers)
        assert check.status_code == 200

        # 5. Refresh token
        refresh_resp = await ac.get("/api/auth/refresh_token",
                                    headers={"Authorization": f"Bearer {access}"})
        assert refresh_resp.status_code == 200

        # 6. CRUD contacts
        contact = {
            "first_name": "Petro",
            "last_name": "Ivanenko",
            "email": "petro@example.com",
            "phone": "123456",
            "birthday": "1990-06-23"
        }
        create = await ac.post("/api/contacts/", json=contact, headers=headers)
        assert create.status_code == 201
        cid = create.json()["id"]

        birthdays = await ac.get("/api/contacts/birthdays/", headers=headers)
        assert birthdays.status_code == 200

        # отримання одного контакту
        get_contacts = await ac.get(f"/api/contacts/{cid}", headers=headers)
        assert get_contacts.status_code == 200
        contact_data = get_contacts.json()
        assert contact_data["id"] == cid

        # оновлення
        update_data = {
            "first_name": "Petro Updated",
            "last_name": "Ivanenko",
            "email": "petro@example.com",
            "phone": "123456",
            "birthday": "1990-06-23",
            "extra_info": "updated info"
        }
        update = await ac.put(f"/api/contacts/{cid}", json=update_data, headers=headers)
        assert update.status_code == 200

        # видалення
        delete = await ac.delete(f"/api/contacts/{cid}", headers=headers)
        assert delete.status_code == 200

        # 7. Reset password (через MailHog)
        reset_req = await ac.post("/api/auth/reset-password-request", json={"email": user_data["email"]})
        assert reset_req.status_code == 200

        reset_token = extract_token_from_mailhog("reset-password")
        reset = await ac.post(f"/api/auth/reset-password/{reset_token}", json={"new_password": "newpass123"})
        assert reset.status_code == 200

        # Перевірка логіну з новим паролем
        login_new = await ac.post(
            "/api/auth/login",
            json={"email": user_data["email"], "password": "newpass123"}
        )
        assert login_new.status_code == 200

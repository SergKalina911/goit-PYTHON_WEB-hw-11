""" Юніт-тести для src.services.email """

import pytest
from fastapi_mail.errors import ConnectionErrors
from src.services import email

class DummyFastMail:
    def __init__(self, conf):
        self.sent = []
    async def send_message(self, message, template_name=None):
        self.sent.append((message, template_name))

@pytest.mark.asyncio
async def test_send_verification_email_success(monkeypatch):
    dummy = DummyFastMail(email.conf)
    monkeypatch.setattr(email, "FastMail", lambda conf: dummy)

    await email.send_verification_email(
        email="test@example.com",
        username="tester",
        host="http://localhost/",
        token="abc123"
    )

    assert dummy.sent, "Message was not sent"
    msg, template = dummy.sent[0]
    assert template == "email_template.html"
    assert msg.subject == "Confirm your email"
    assert "abc123" in msg.template_body["token"]

@pytest.mark.asyncio
async def test_send_reset_password_email_success(monkeypatch):
    dummy = DummyFastMail(email.conf)
    monkeypatch.setattr(email, "FastMail", lambda conf: dummy)

    await email.send_reset_password_email(
        email="test@example.com",
        host="http://localhost/",
        token="xyz789"
    )

    assert dummy.sent, "Message was not sent"
    msg, template = dummy.sent[0]
    assert template == "reset_password.html"
    assert "xyz789" in msg.template_body["reset_link"]

@pytest.mark.asyncio
async def test_send_verification_email_failure(monkeypatch, capsys):
    class FailingFastMail:
        async def send_message(self, *args, **kwargs):
            raise ConnectionErrors("SMTP error")

    monkeypatch.setattr(email, "FastMail", lambda conf: FailingFastMail())

    await email.send_verification_email(
        email="fail@example.com",
        username="tester",
        host="http://localhost/",
        token="badtoken"
    )

    captured = capsys.readouterr()
    assert "SMTP error" in captured.out

@pytest.mark.asyncio
async def test_send_reset_password_email_failure(monkeypatch, capsys):
    class FailingFastMail:
        async def send_message(self, *args, **kwargs):
            raise ConnectionErrors("SMTP fail")

    monkeypatch.setattr(email, "FastMail", lambda conf: FailingFastMail())

    await email.send_reset_password_email(
        email="fail@example.com",
        host="http://localhost/",
        token="badtoken"
    )

    captured = capsys.readouterr()
    assert "SMTP fail" in captured.out

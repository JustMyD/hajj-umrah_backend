from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from src.core.auth.ports.email_sender import EmailSender


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        sender_from: str,
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender_from = sender_from
        self.use_tls = use_tls

    async def send_magic_link(self, *, to_email: str, magic_link_url: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = "Ваш вход в сервис"
        msg["From"] = self.sender_from
        msg["To"] = to_email
        msg.set_content(f"Ссылка для входа (действует ограниченное время):\n\n{magic_link_url}\n")

        await asyncio.to_thread(self._send, msg)

    async def send_email_change_link(self, *, to_email: str, email_change_url: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = "Подтверждение смены email"
        msg["From"] = self.sender_from
        msg["To"] = to_email
        msg.set_content(f"Подтвердите смену email по ссылке (действует ограниченное время):\n\n{email_change_url}\n")

        await asyncio.to_thread(self._send, msg)

    def _send(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            if self.use_tls:
                smtp.starttls()
            if self.user:
                smtp.login(self.user, self.password)
            smtp.send_message(msg)



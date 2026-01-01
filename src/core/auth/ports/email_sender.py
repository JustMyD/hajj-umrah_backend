from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send_magic_link(self, *, to_email: str, magic_link_url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_email_change_link(self, *, to_email: str, email_change_url: str) -> None:
        raise NotImplementedError



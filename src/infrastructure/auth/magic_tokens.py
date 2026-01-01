from __future__ import annotations

import hashlib
import hmac


def hash_token(*, token: str, pepper: str) -> str:
    """
    Универсальная функция для хеширования токенов (magic link, refresh, email change).
    Использует HMAC-SHA256 для безопасного хранения в БД.
    """
    return hmac.new(pepper.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()



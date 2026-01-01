from __future__ import annotations

from typing import Any

import httpx

from src.core.auth.entities.oauth_profile import OAuthProfile
from src.core.auth.ports.oauth_validator import OAuthValidator


class OAuthValidationError(ValueError):
    pass


class HttpxOAuthValidator(OAuthValidator):
    """
    MVP: поддерживаем только Google, потому что фронт может присылать access_token или id_token.
    Для остальных провайдеров пока возвращаем ошибку (можно расширить позже).
    """

    async def validate(self, *, provider: str, access_token: str, id_token: str | None = None) -> OAuthProfile:
        provider = provider.lower().strip()
        if provider == "google":
            if id_token:
                data = await self._google_tokeninfo(id_token=id_token)
            else:
                data = await self._google_userinfo(access_token=access_token)

            sub = data.get("sub")
            if not sub:
                raise OAuthValidationError("google did not return sub")
            email = data.get("email")
            email_verified = data.get("email_verified")
            name = data.get("name") or data.get("given_name")
            return OAuthProfile(
                provider="google",
                provider_account_id=str(sub),
                email=str(email) if email else None,
                email_verified=bool(email_verified) if email_verified is not None else None,
                full_name=str(name) if name else None,
            )

        if provider == "yandex":
            data = await self._yandex_info(access_token=access_token)
            yid = data.get("id")
            if not yid:
                raise OAuthValidationError("yandex did not return id")
            email = data.get("default_email") or (data.get("emails") or [None])[0]
            full_name = data.get("real_name") or data.get("display_name")
            return OAuthProfile(
                provider="yandex",
                provider_account_id=str(yid),
                email=str(email) if email else None,
                email_verified=True if email else None,
                full_name=str(full_name) if full_name else None,
            )

        if provider == "vk":
            data = await self._vk_users_get(access_token=access_token)
            # VK API: {"response":[{"id":..., "first_name":..., "last_name":...}]}
            resp = data.get("response") or []
            if not resp:
                raise OAuthValidationError("vk did not return user info")
            u = resp[0]
            uid = u.get("id")
            if not uid:
                raise OAuthValidationError("vk did not return id")
            first = u.get("first_name") or ""
            last = u.get("last_name") or ""
            full_name = (f"{first} {last}").strip() or None
            return OAuthProfile(
                provider="vk",
                provider_account_id=str(uid),
                email=None,  # VK обычно не отдаёт email по одному access_token
                email_verified=None,
                full_name=full_name,
            )

        raise OAuthValidationError(f"provider '{provider}' is not supported")

    async def _google_userinfo(self, *, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if resp.status_code != 200:
            raise OAuthValidationError("invalid google access_token")
        return resp.json()

    async def _google_tokeninfo(self, *, id_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token})
        if resp.status_code != 200:
            raise OAuthValidationError("invalid google id_token")
        return resp.json()

    async def _yandex_info(self, *, access_token: str) -> dict[str, Any]:
        # https://login.yandex.ru/info
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://login.yandex.ru/info",
                params={"format": "json"},
                headers={"Authorization": f"OAuth {access_token}"},
            )
        if resp.status_code != 200:
            raise OAuthValidationError("invalid yandex access_token")
        return resp.json()

    async def _vk_users_get(self, *, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.vk.com/method/users.get",
                params={"v": "5.131", "access_token": access_token},
            )
        if resp.status_code != 200:
            raise OAuthValidationError("invalid vk access_token")
        data = resp.json()
        if "error" in data:
            raise OAuthValidationError("invalid vk access_token")
        return data



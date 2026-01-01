from __future__ import annotations

from uuid import UUID
from typing import Optional, List
from datetime import date

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[date] = None
    email_notification: bool = True
    sms_notification: bool = True
    favorite_tour_ids: List[UUID] = Field(default_factory=list)
    comparison_tour_ids: List[UUID] = Field(default_factory=list)


class UpdateMeRequest(BaseModel):
    name: Optional[str] = Field(default=None)
    surname: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    birth_date: Optional[date] = Field(default=None)
    email_notification: Optional[bool] = Field(default=None)
    sms_notification: Optional[bool] = Field(default=None)


class EmailChangeStartRequest(BaseModel):
    new_email: str = Field(min_length=3)


class EmailChangeConfirmRequest(BaseModel):
    token: str = Field(min_length=10)


class OkResponse(BaseModel):
    ok: bool = True


class AddToUserListRequest(BaseModel):
    tour_id: UUID


class RemoveFromUserListRequest(BaseModel):
    tour_id: UUID


class MergeUserListRequest(BaseModel):
    tour_ids: List[UUID]

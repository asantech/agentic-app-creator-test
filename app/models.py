from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ConfirmationRequest(BaseModel):
    preview_id: str = Field(min_length=1)
    confirm: bool = False


class OperationResponse(BaseModel):
    status: str
    preview_id: str | None = None
    deleted: list[str] = []
    excluded: list[str] = []
    failures: list[str] = []
    counts: dict[str, int] = {}
    remaining_unknown: bool = False
    message: str = ""
    verification_error: str | None = None
    details: dict[str, Any] = {}

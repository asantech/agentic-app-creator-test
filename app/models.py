from __future__ import annotations

from typing import Any
from pydantic import BaseModel, StrictBool


class DeleteRequest(BaseModel):
    confirmation: StrictBool


class OperationResponse(BaseModel):
    status: str
    root: str | None = None
    deletable: list[str] = []
    deleted: list[str] = []
    excluded: list[str] = []
    failures: list[dict[str, str]] = []
    counts: dict[str, int | None] = {}
    remaining_unknown: bool = False
    error: str | None = None
    verification_error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()

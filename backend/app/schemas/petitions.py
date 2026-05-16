from __future__ import annotations

from pydantic import BaseModel


class PetitionSubmitResponse(BaseModel):
    petition_code: str
    message_ar: str


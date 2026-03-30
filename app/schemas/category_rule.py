import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CategoryRuleCreate(BaseModel):
    merchant_pattern: str = Field(..., min_length=1, max_length=200)
    match_type: Literal["exact", "partial", "keyword"]
    category: str = Field(..., min_length=1, max_length=100)


class CategoryRuleResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    merchant_pattern: str
    match_type: str
    category: str
    created_at: datetime

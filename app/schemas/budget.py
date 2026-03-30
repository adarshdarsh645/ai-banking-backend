import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    amount_limit: Decimal = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)


class BudgetResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    amount_limit: Decimal
    month: int
    year: int
    created_at: datetime


class BudgetProgressResponse(BaseModel):
    budget: BudgetResponse
    spent: Decimal
    progress_percentage: float

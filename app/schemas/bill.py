import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BillCreate(BaseModel):
    biller_name: str = Field(..., min_length=1, max_length=150)
    due_date: date
    amount_due: Decimal = Field(..., gt=0)
    auto_pay: bool = False


class BillUpdate(BaseModel):
    biller_name: str | None = Field(None, min_length=1, max_length=150)
    due_date: date | None = None
    amount_due: Decimal | None = Field(None, gt=0)
    status: Literal["upcoming", "paid", "overdue"] | None = None
    auto_pay: bool | None = None


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    biller_name: str
    due_date: date
    amount_due: Decimal
    status: str
    auto_pay: bool
    created_at: datetime

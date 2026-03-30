import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


AccountType = Literal["savings", "checking", "credit_card", "investment", "loan"]


class AccountCreate(BaseModel):
    bank_name: str = Field(..., min_length=2, max_length=120)
    account_type: AccountType
    masked_account: str = Field(
        ..., min_length=4, max_length=20, description="e.g. ****1234"
    )
    currency: str = Field(default="USD", min_length=3, max_length=3)
    balance: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0"))


class AccountResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    bank_name: str
    account_type: str
    masked_account: str
    currency: str
    balance: Decimal
    created_at: datetime


class AccountListResponse(BaseModel):
    total: int
    items: list[AccountResponse]

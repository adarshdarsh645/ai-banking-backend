import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


TxnType = Literal["debit", "credit"]


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    description: str = Field(..., min_length=1, max_length=500)
    category: str = Field(default="Uncategorized", max_length=100)
    amount: Decimal = Field(..., gt=Decimal("0"))
    currency: str = Field(default="USD", min_length=3, max_length=3)
    txn_type: TxnType
    merchant: str | None = Field(default=None, max_length=200)
    txn_date: date
    posted_date: date | None = None


class TransactionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    account_id: uuid.UUID
    description: str
    category: str
    amount: Decimal
    currency: str
    txn_type: str
    merchant: str | None
    txn_date: date
    posted_date: date | None
    created_at: datetime


class TransactionFilter(BaseModel):
    account_id: uuid.UUID | None = None
    txn_type: TxnType | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TransactionResponse]


class CSVImportResult(BaseModel):
    imported: int
    failed: int
    errors: list[str]


class TransactionRecategorize(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    create_rule: bool = Field(default=False, description="Auto-create category rule for future transactions")


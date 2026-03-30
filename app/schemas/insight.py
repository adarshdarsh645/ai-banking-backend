import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class CashflowMonth(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal


class CashflowResponse(BaseModel):
    data: list[CashflowMonth]


class MerchantSpend(BaseModel):
    merchant: str
    total: Decimal


class TopMerchantsResponse(BaseModel):
    data: list[MerchantSpend]


class CategorySpend(BaseModel):
    category: str
    total: Decimal


class CategorySpendResponse(BaseModel):
    data: list[CategorySpend]


class BurnRateItem(BaseModel):
    category: str
    budget_limit: Decimal
    spent: Decimal
    progress_pct: float


class BurnRateResponse(BaseModel):
    data: list[BurnRateItem]


class TransactionExportRow(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    description: str
    category: str
    amount: Decimal
    currency: str
    txn_type: str
    merchant: str | None
    txn_date: date
    created_at: datetime

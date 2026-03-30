from decimal import Decimal

from pydantic import BaseModel


class SpendingByCategory(BaseModel):
    category: str
    total_spent: Decimal


class ReportResponse(BaseModel):
    month: int | None
    year: int | None
    spending: list[SpendingByCategory]


class CurrencyRatesResponse(BaseModel):
    base: str
    rates: dict[str, float | None]
    fallback: bool = False

